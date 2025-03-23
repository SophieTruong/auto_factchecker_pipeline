from datetime import datetime
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from database.crud import (
    insert_source_document,
    get_source_document_by_text,
    insert_claims,
    update_claim,
    delete_claims,
    get_claim_by_text,
    get_claims_by_created_at,
    get_claim_detection_model_by_name,
    insert_claim_detection_model,
    insert_claim_model_inference
)

from models.source_document import SourceDocumentCreate, SourceDocument
from models.claim import ClaimCreate, Claim
from models.claim_model_inference import ClaimModelInferenceCreate, ClaimModelInference
from models.claim_detection_model import ClaimDetectionModel
from models.claim_detection_response import BatchClaimResponse, ClaimResponse

from utils.sentencizer import get_sentences
from utils.make_request import make_request
from utils.app_logging import logger
from utils.validator import validate_date_range

from services.claim_prediction_rcp_client import ClaimPredictionRcpClient
from services.publish_monitoring_event import PublishMonitoringEvent
class ClaimDetectionService:
    def __init__(self, db: Session, inference_service_uri: str):
        self.db = db
        self.inference_service_uri = inference_service_uri
        # Initialize clients but don't connect yet
        self.claim_prediction_client = ClaimPredictionRcpClient()
        self.publish_monitoring_event = PublishMonitoringEvent()

    async def ensure_connections(self):
        """Ensure all RabbitMQ connections are established"""
        if not self.claim_prediction_client.is_connected:
            await self.claim_prediction_client.connect()
            
        if not self.publish_monitoring_event.is_connected:
            await self.publish_monitoring_event.connect()
            
    async def close_connections(self):
        """Close all RabbitMQ connections"""
        if hasattr(self, 'claim_prediction_client') and self.claim_prediction_client.is_connected:
            await self.claim_prediction_client.close()
            
        if hasattr(self, 'publish_monitoring_event') and self.publish_monitoring_event.is_connected:
            await self.publish_monitoring_event.close()

    async def get_predictions(
        self, 
        input_data: SourceDocumentCreate
    ) -> Optional[BatchClaimResponse]:
        """
        Process a source document to extract and classify claims.
        
        Args:
            input_data: Source document data
            
        Returns:
            BatchClaimResponse containing claims and their classifications
        """
        try:
            with self.db.begin():
                # Insert source document
                source_document = self._create_source_document(input_data)
                
                if not source_document:
                    raise Exception("*** Failed to insert source document. Try editing the input text.")
                
                # Process claims
                claims = self._create_claims(source_document.id, input_data.text)
                logger.info(f"*** claims after self._create_claims: {claims}")
                
                # Get model predictions   
                predictions = await self._process_predictions(claims)

                return self._create_response(claims, predictions)
        except Exception as e:
            self.db.rollback()
            raise Exception(f"{e}")

    async def update_claims(self, claims: List[Claim]) -> Optional[BatchClaimResponse]:
        """Update claims in database and update claim predictions if applicable"""
        try:
            # Use the shared monitoring event publisher
            await self.ensure_connections()
            
            with self.db.begin():
                if len(claims) > 0:        
                    # Update claims in database
                    to_update = []
                    to_delete = []
                    updated_claims = []
                    for claim in claims:
                        if claim.text.strip():
                            to_update.append(claim)
                        else:
                            to_delete.append(claim.id)
                    # Batch delete empty claims
                    if len(to_delete) > 0:
                        deleted_claims = delete_claims(self.db, to_delete)
                        logger.info(f"*** deleted claim: {deleted_claims}")
                        
                        await self.publish_monitoring_event.publish_event(
                            event_type="deleted",
                            module_name="claim_detection",
                            event_data={"deleted_counts": len(deleted_claims)}
                        )

                    # Iterate update non-empty claims
                    if len(to_update) > 0:
                        for claim in to_update:
                            logger.info(f"*** claim to be updated: {claim}")
                            updated_claim = update_claim(self.db, claim.model_dump())
                            updated_claims.append(updated_claim)
                            logger.info(f"*** updated claim: {updated_claim}")
                        
                        await self.publish_monitoring_event.publish_event(
                            event_type="updated",
                            module_name="claim_detection",
                            event_data={"updated_counts": len(updated_claims)}
                        )
                                
                    # Get model predictions
                    if len(updated_claims) > 0:
                        predictions = await self._process_predictions(updated_claims)
                        logger.info(f"*** predictions: {predictions}")
                                        
                    return self._create_response(updated_claims, predictions)
                else:
                    return None
        except Exception as e:
            self.db.rollback()
            raise Exception(f"{e}")
    
    async def get_claims(self, start_date: datetime, end_date: datetime) -> Optional[List[Claim]]:
        """Get claims by date range."""
        try:
            validate_date_range(start_date, end_date)
            claims = get_claims_by_created_at(db=self.db, start_date=start_date, end_date=end_date)
            return claims
        except Exception as e:
            raise Exception(f"{e}")

    def _create_source_document(self, input_data: SourceDocumentCreate) -> Optional[SourceDocument]:
        """Create source document record."""
        logger.info(f"*** input_data: {input_data}")
        inserted_source_document = insert_source_document(self.db, input_data.model_dump())
        
        if not inserted_source_document:
            return get_source_document_by_text(self.db, input_data.text)
        
        return inserted_source_document
        
    def _create_claims(self, source_document_id: UUID, text: str) -> List[Claim]:
        """
        Extract and create claims from source text.
        
        Args:
            source_document_id: UUID of the source document
            text: Source text to extract claims from
            
        Returns:
            List of Claim objects, either newly inserted or existing
        """
        # Get sentences and create claim objects
        claims = [
            ClaimCreate(
                text=txt, 
                source_document_id=source_document_id
            ) 
            for txt in get_sentences(text) 
            if txt.strip() and len(txt.strip()) > 5
        ]
        claims_data = [claim.model_dump() for claim in claims]

        inserted_claims = insert_claims(self.db, claims_data)

        # Create a mapping of text to claim for efficient lookup
        claim_map = {claim.text: claim for claim in inserted_claims}

        # Return claims in original order, using either inserted or existing claims
        return [
            claim_map.get(claim.text) or get_claim_by_text(self.db, claim.text)
            for claim in claims
        ]
    
    async def _process_predictions(self, claims: List[Claim]) -> List[ClaimModelInference]:
        """Get and store model predictions for claims."""
        # Get model predictions
        
        # inference_res = await self._get_model_predictions(claims) # DEPRECATED
        
        inference_res = await self._get_model_predictions_from_rabbitmq(claims)
                
        inference_res = json.loads(inference_res)
        
        for res in inference_res["inference_results"]:
            
            res["created_at"] = datetime.strptime(res["created_at"], "%Y-%m-%d %H:%M:%S")
            
        logger.info(f"*** inference_res from rabbitmq: {inference_res}")
        
        # Get or create model record
        model_id = self._get_or_create_model(inference_res["model_metadata"])
        
        # Create and store predictions
        return self._insert_predictions(claims, model_id, inference_res)

    async def _get_model_predictions(self, claims: List[Claim]) -> dict:
        """Get predictions from inference service."""
        return await make_request(
            self.inference_service_uri,
            [claim.text for claim in claims]
        )

    async def _get_model_predictions_from_rabbitmq(self, claims: List[Claim]) -> dict:
        """Get predictions from inference service."""
        # Use the already initialized client
        await self.ensure_connections()
        
        logger.info("*** claim_prediction_rpc_client ready")
        
        return await self.claim_prediction_client.get_model_predictions(
            [claim.text for claim in claims]
        )

    def _get_or_create_model(self, model_metadata: dict) -> UUID:
        """Get existing model ID or create new model record."""
        model = ClaimDetectionModel(
            name=model_metadata["model_name"],
            version=model_metadata["model_version"],
            model_path=model_metadata["model_path"],
            created_at=model_metadata["created_at"]
        )
        
        existing_model = get_claim_detection_model_by_name(self.db, model.name)
        if existing_model:
            return existing_model.id
            
        inserted_model = insert_claim_detection_model(self.db, model.model_dump())
        
        return inserted_model.id

    def _insert_predictions(
        self, 
        claims: List[Claim], 
        model_id: UUID, 
        inference_res: dict
    ) -> List[ClaimModelInference]:
        """Store model predictions in database."""
        predictions = [
            ClaimModelInferenceCreate(
                claim_id=claim.id,
                claim_detection_model_id=model_id,
                label=inference_res["inference_results"][i]["label"] == 1 # cast int to bool
            )
            for i, claim in enumerate(claims)
        ]
        
        return insert_claim_model_inference(
            self.db, 
            [pred.model_dump() for pred in predictions]
        )

    def _create_response(
        self, 
        claims: List[Claim],  
        predictions: List[ClaimModelInference]
    ) -> BatchClaimResponse:
        """Create API response object."""
        return BatchClaimResponse(
            claims=[
                ClaimResponse(claim=claim, inference=inference)
                for claim, inference in zip(claims, predictions)
            ]
        )
