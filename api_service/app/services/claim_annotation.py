from typing import List, Optional
from uuid import UUID   

from sqlalchemy.orm import Session

from database.crud import (
    insert_annotation_session,
    insert_claim_annotation,
    update_claim_annotation
)

from models.claim_annotation import ClaimAnnotation, ClaimAnnotationCreate
from models.claim_annotation_input import BatchClaimAnnotationInput
from utils.app_logging import logger

class ClaimAnnotationService:
    def __init__(self, db: Session):
        self.db = db

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
                logger.info(f"Created annotation session with ID: {annotation_session_id}")
                
                inserted_claim_annotations = self._create_claim_annotations(claim_annotation_inputs, annotation_session_id)
                logger.info(f"Created claim annotations: {inserted_claim_annotations}")                
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
                    updated_claim_annotation = update_claim_annotation(
                        self.db, 
                        claim_annotation.annotation_session_id, 
                        claim_annotation.claim_id, 
                        claim_annotation.model_dump())
                    updated_claim_annotations.append(updated_claim_annotation)
                return updated_claim_annotations
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
        return inserted_claim_annotations
