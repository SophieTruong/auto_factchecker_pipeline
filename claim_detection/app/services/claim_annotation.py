from typing import List, Optional
from uuid import UUID   

from sqlalchemy.orm import Session

from database.crud import (
    insert_annotation_session,
    insert_claim_annotation,
    update_claim_annotation,
    get_claim_model_inference_by_claim_id
)

from models.claim_annotation import ClaimAnnotation, ClaimAnnotationCreate
from models.claim_annotation_input import BatchClaimAnnotationInput

from services.publish_monitoring_event import PublishMonitoringEvent

from utils.app_logging import logger

class ClaimAnnotationService:
    def __init__(self, db: Session):
        self.db = db
        self.publish_monitoring_event = PublishMonitoringEvent()
    async def create_claim_annotation(self, claim_annotation_inputs: BatchClaimAnnotationInput) -> Optional[List[ClaimAnnotation]]:
        """
        Create a claim annotation.
        
        Args:
            claim_annotation_inputs (BatchClaimAnnotationInput): Claim annotation inputs
        
        Returns:
            Optional[List[ClaimAnnotation]]: A list of claim annotations
        """
        
        try:            
            with self.db.begin():
                
                annotation_session_id = insert_annotation_session(self.db)
                
                # Return a list of Pydantic ClaimAnnotation objects                                                
                inserted_claim_annotations = self._create_claim_annotations(claim_annotation_inputs, annotation_session_id)
                
                logger.info(f"Created claim annotations: {inserted_claim_annotations}")            
                
                claim_ids = [str(claim.claim_id) for claim in inserted_claim_annotations]
                
                claim_annotations = [claim.binary_label for claim in inserted_claim_annotations]
                
                # Insert claim model inferences and annotations to monitoring service
                # Return a list of SQLAlchemy ClaimModelInference objects
                claim_model_inferences = [get_claim_model_inference_by_claim_id(self.db, claim_id) for claim_id in claim_ids]
                
                logger.info(f"*** MYDEBUG_claim_model_inferences: {claim_model_inferences}")
                
                claim_model_labels = [claim_model_inference.label for claim_model_inference in claim_model_inferences]
                
                claim_model_ids = [str(claim_model_inference.claim_detection_model_id) for claim_model_inference in claim_model_inferences]
                
                message = {
                    "claim_ids": claim_ids,
                    "claim_annotations": claim_annotations,
                    "claim_model_inferences": claim_model_labels,
                    "claim_model_ids": claim_model_ids
                }
                
                logger.info(f"Message to be published to publish_monitoring_event: {message}")
                
                await self.publish_monitoring_event.publish_event(
                    event_type="created",
                    module_name="claim_annotation",
                    event_data=message
                )
                                
                return inserted_claim_annotations
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"{e}")
    
    async def update_claim_annotation(self, claim_annotation_inputs: List[ClaimAnnotation]) -> Optional[List[ClaimAnnotation]]:
        """
        Update a claim annotation.
        """
        try:
            with self.db.begin():
                
                updated_claim_annotations = []
                
                for claim_annotation in claim_annotation_inputs:
                
                    logger.info(f"*** claim_annotation to be updated: {claim_annotation.model_dump()}")

                    # TODO: Batch update
                    updated_claim_annotation = update_claim_annotation(
                
                        self.db, 
                
                        claim_annotation.annotation_session_id, 
                
                        claim_annotation.claim_id, 
                
                        claim_annotation.model_dump())

                    if updated_claim_annotation is not None:
                        
                        updated_claim_annotations.append(updated_claim_annotation)
                
                if len(updated_claim_annotations) > 0:
                    updated_claim_annotations_pydantic = [ClaimAnnotation.model_validate(claim_annotation) for claim_annotation in updated_claim_annotations]
                    
                    # TODO: How do claim annotation updates affects metrics?
                    # TODO: Should there be a new updated event for this? self.publish_monitoring_event.publish_event ... 
                    
                    return updated_claim_annotations_pydantic
                
                else:
                    return None
        
        except Exception as e:
            
            self.db.rollback()
            
            raise Exception(f"{e}")
        
    def _create_claim_annotations(self, claim_annotations: BatchClaimAnnotationInput, annotation_session_id: UUID) -> List[ClaimAnnotation]:
        
        claim_annotations_data = [
        
            ClaimAnnotationCreate(
        
                source_document_id=input.source_document_id,
        
                claim_id=input.claim_id,
        
                annotation_session_id=annotation_session_id,
        
                binary_label=input.binary_label,
        
                text_label=input.text_label
        
            ).model_dump() for input in claim_annotations.claims
        
        ]
        
        inserted_claim_annotations = insert_claim_annotation(self.db, claim_annotations_data)
        
        inserted_claim_annotations_pydantic = [ClaimAnnotation.model_validate(claim_annotation) for claim_annotation in inserted_claim_annotations]
        
        return inserted_claim_annotations_pydantic
