from datetime import datetime
import json
from typing import List, Optional

from models.source_document import SourceDocumentCreate
from models.claim import Claim
from models.claim_detection_response import BatchClaimResponse
from models.claim_annotation_input import BatchClaimAnnotationInput
from models.claim_annotation import ClaimAnnotation

from utils.app_logging import logger

# To this (using relative imports):
from .claim_detection_rcp_client import ClaimDetectionRCPClient

class ClaimDetectionService:
    
    def __init__(self):        
        # RabbitMQ connection pool: 1 connection
        # Initialize RCP client:
        self.claim_detection_client = ClaimDetectionRCPClient()
        
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
            
            # RCP call to claim detection RCP server
            insert_res = await self.claim_detection_client.publish_message(
                data=input_data.model_dump(),
                request_type="claim_detection_insert"
            )
            
            insert_res = json.loads(insert_res)
            
            if insert_res.get("status") == "error":
                
                raise Exception(f"{insert_res.get('message')}")
            
            logger.info(f"*** insert_res: {insert_res}")

            return BatchClaimResponse(**insert_res)
        
        except Exception as e:
            
            raise Exception(f"{e}")

    async def update_predictions(self, claims: List[Claim]) -> Optional[BatchClaimResponse]:
        """Update claims and its predictions in database"""
        try:
                        
            new_claims = [claim.model_dump() for claim in claims]
            
            # RCP call to claim detection RCP server                        
            insert_res = await self.claim_detection_client.publish_message(
                data=new_claims,
                request_type="claim_detection_update"
            )
            
            insert_res = json.loads(insert_res)
            
            if insert_res.get("status") == "error":
                
                raise Exception(f"{insert_res.get('message')}")
            
            logger.info(f"*** insert_res: {insert_res}")
            
            return BatchClaimResponse(**insert_res)
                    
        except Exception as e:
            
            raise Exception(f"{e}")
            
    async def get_claims(self, start_date: datetime, end_date: datetime) -> Optional[List[Claim]]:
        """Get claims by date range."""
        try:
            
            # RCP call to claim detection RCP server
            claims = await self.claim_detection_client.publish_message(
                data={"start_date": start_date, "end_date": end_date},
                request_type="claim_detection_get"
            )
            
            claims = json.loads(claims)
            
            logger.info(f"*** claims: {claims}")
            
            if claims and isinstance(claims, list):
                
                logger.info(f"*** claims is a list")
                
                return [Claim(**claim) for claim in claims]
            
            return []
        
        except Exception as e:
            
            raise Exception(f"{e}")
        
    async def create_claim_annotation(self, claim_annotation_inputs: BatchClaimAnnotationInput) -> Optional[List[ClaimAnnotation]]:
        """Create claim annotations"""
        try:
            
            # RCP call to claim detection RCP server
            claim_annotations = await self.claim_detection_client.publish_message(
                data=claim_annotation_inputs.model_dump(),
                request_type="claim_annotation_insert"
            )
            
            claim_annotations = json.loads(claim_annotations)
            
            if isinstance(claim_annotations, dict) and claim_annotations.get("status") == "error":
                
                raise Exception(f"{claim_annotations.get('message')}")
            
            logger.info(f"*** NEW create_claim_annotation: {claim_annotations}")
                                        
            return [ClaimAnnotation(**claim_annotation) for claim_annotation in claim_annotations]
        
        except Exception as e:
            
            raise Exception(f"{e}")
        
    async def update_claim_annotation(self, claim_annotation_inputs: List[ClaimAnnotation]) -> Optional[List[ClaimAnnotation]]:
        """Update claim annotations"""
        try:
            
            # RCP call to claim detection RCP server
            claim_annotations = await self.claim_detection_client.publish_message(
                data=[claim_annotation.model_dump() for claim_annotation in claim_annotation_inputs],
                request_type="claim_annotation_update"
            )
            
            claim_annotations = json.loads(claim_annotations)
            
            if isinstance(claim_annotations, dict) and claim_annotations.get("status") == "error":
                
                raise Exception(f"{claim_annotations.get('message')}")
            
            logger.info(f"*** NEW update_claim_annotation: {claim_annotations}")
                                        
            return [ClaimAnnotation(**claim_annotation) for claim_annotation in claim_annotations] if claim_annotations else None
        
        except Exception as e:
            
            raise Exception(f"{e}")