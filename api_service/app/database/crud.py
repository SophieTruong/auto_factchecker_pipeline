import sys
print(f"*** sys.path: {sys.path}")
from utils.app_logging import logger

from typing import List, Optional
from datetime import datetime
import traceback

from sqlalchemy.orm import Session
from uuid import UUID

from .models import (
    AnnotationSession,
    Claim, 
    ClaimModelInference, 
    ClaimDetectionModel, 
    ClaimAnnotation,
    SourceDocument, 
)

from .queries import (
    # Source Document Queries
    insert_source_document_query,
    get_source_document_by_id_query,
    get_source_document_by_text_query,
    update_source_document_query,
    delete_source_document_query,
    # Claim Queries
    get_claim_by_id_query, 
    get_claim_by_text_query, 
    get_claims_by_time_range_query, 
    insert_claims_query,
    update_claim_query, 
    delete_claims_query,
    # Claim Model Inference Queries
    insert_claim_model_inference_query,
    get_claim_model_inference_by_id_query,
    get_claim_model_inference_by_claim_id_query,
    update_claim_model_inference_by_claim_id_query,
    update_claim_model_inference_query,
    delete_claim_model_inference_query,
    # Claim Detection Model Queries
    insert_claim_detection_model_query,
    get_claim_detection_model_by_id_query,
    get_claim_detection_model_by_name_query,
    update_claim_detection_model_query,
    delete_claim_detection_model_query,
    # Annotation Session Queries
    insert_annotation_session_query,
    get_annotation_session_by_id_query,
    update_annotation_session_query,
    delete_annotation_session_query,
    # Claim Annotation Queries
    insert_claim_annotation_query,
    get_claim_annotation_by_claim_id_query,
    get_claim_annotation_by_source_document_id_query,
    get_claim_annotation_by_annotation_session_id_query,
    update_claim_annotation_query,
    delete_claim_annotation_query,
    # Claim with Inference and Annotation Queries
    get_claims_with_inference_and_annotation_query,
)

## Source Document CRUD Operations
def get_source_document_by_id(db: Session, source_document_id: UUID) -> Optional[SourceDocument]:
    """
    Retrieve a source document from the database by its ID.
    """
    try:
        return db.scalar(get_source_document_by_id_query(source_document_id))
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def get_source_document_by_text(db: Session, text: str) -> Optional[SourceDocument]:
    """
    Retrieve a source document from the database by its text.
    """
    try:
        return db.scalar(get_source_document_by_text_query(text))
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def insert_source_document(db: Session, source_document_data: dict) -> Optional[SourceDocument]:
    """
    Insert a source document into the database.
    """
    if not source_document_data or not isinstance(source_document_data, dict):
        raise ValueError("source_document_data must be a non-empty dictionary")
    
    try:
        inserted_source_document = db.scalar(insert_source_document_query(source_document_data))
        return inserted_source_document
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def update_source_document(db: Session, source_document_id: UUID, source_document_data: dict) -> Optional[SourceDocument]:
    """
    Update a source document in the database by its ID.
    """
    try:
        updated_source_document = db.scalar(update_source_document_query(source_document_id, source_document_data))
        db.commit()
        return updated_source_document
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

def delete_source_document(db: Session, source_document_id: UUID) -> Optional[SourceDocument]:
    """
    Delete a source document from the database by its ID.
    """
    try:
        deleted_source_document = db.scalar(delete_source_document_query(source_document_id))
        db.commit()
        return deleted_source_document
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")


## Claim CRUD Operations
def get_claim_by_id(db: Session, claim_id:UUID) -> Optional[Claim]:
    """
    Retrieve a claim from the database by its ID.

    Args:
        db (Session): Database session
        claim_id (UUID): ID of the claim to retrieve

    Returns:
        Optional[Claim]: The claim if found, None otherwise
    """   
    try:
        return db.scalar(get_claim_by_id_query(claim_id))
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def get_claim_by_text(db: Session, text: str) -> Optional[Claim]:
    """
    Retrieve claims from the database by their text.
    
    Args:
        db (Session): Database session
        text (str): Text of the claim to retrieve

    Returns:
        List[Claim]: List of claims with the specified text
    """    
    try:
        query = get_claim_by_text_query(text)
        return db.scalar(query)
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def get_claims_by_created_at(db: Session, start_date: datetime, end_date: datetime) -> Optional[List[Claim]]:
    """
    Retrieve claims from the database by their creation date range.
    
    Args:
        db (Session): Database session
        start_date (datetime): Start date of the range
        end_date (datetime): End date of the range

    Returns:
        List[Claim]: List of claims within the specified date range
    """        
    if start_date > end_date:
        raise ValueError("start_date cannot be later than end_date")
    try:
        return db.scalars(get_claims_by_time_range_query(start_date, end_date)).all()
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def insert_claims(db: Session, claims_data: List[dict]) -> Optional[List[Claim]]:
    """
    Bulk insert multiple fact-checked claims into the database.

    Args:
        db (Session): Database session
        claims_data (List[dict]): List of claim dictionaries to insert

    Returns:
        List[dict]: List of inserted claims with their assigned IDs
    
    Raises:
        Exception: If database insertion fails
    """    
    try:
        inserted_claims = db.scalars(insert_claims_query(claims_data)).all()
        return inserted_claims    
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")
    
def update_claim(db: Session, claim_data: dict) -> Optional[Claim]:
    """
    Update a claim in the database by its ID.
    """                
    if not claim_data or not isinstance(claim_data, dict):
        raise ValueError("claim_data must be a non-empty dictionary")

    try:
        updated_claim = db.scalar(update_claim_query(claim_data))
        return updated_claim
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"db.scalar fails: {str(e)}")

def delete_claims(db: Session, claim_ids: List[UUID]) -> Optional[List[Claim]]:
    """
    Delete a claim from the database by its ID.
    """
    try:
        deleted_claims = db.scalars(delete_claims_query(claim_ids)).all()
        return deleted_claims
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")
    
## Claim Model Inference CRUD Operations
def get_claim_model_inference_by_id(db: Session, claim_model_inference_id: UUID) -> Optional[ClaimModelInference]:
    """x
    Retrieve a claim model inference from the database by its ID.
    """
    try:
        return db.scalar(get_claim_model_inference_by_id_query(claim_model_inference_id))
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def get_claim_model_inference_by_claim_id(db: Session, claim_id: UUID) -> Optional[ClaimModelInference]:
    """
    Retrieve a claim model inference from the database by its claim ID.
    """
    try:
        return db.scalar(get_claim_model_inference_by_claim_id_query(claim_id))
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def insert_claim_model_inference(db: Session, claim_model_inference_data: List[dict]) -> Optional[List[ClaimModelInference]]:
    """
    Insert a claim model inference into the database.
    """
    try:
        return db.scalars(insert_claim_model_inference_query(claim_model_inference_data)).all()
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def update_claim_model_inference(db: Session, claim_model_inference_id: UUID, claim_model_inference_data: dict) -> Optional[ClaimModelInference]:
    """
    Update a claim model inference in the database by its ID.
    """
    try:
        updated_claim_model_inference = db.scalar(update_claim_model_inference_query(claim_model_inference_id, claim_model_inference_data))
        db.commit()
        return updated_claim_model_inference
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

def update_claim_model_inference_by_claim_id(db: Session, claim_id: UUID, claim_model_inference_data: dict) -> Optional[ClaimModelInference]:
    """
    Update a claim model inference in the database by its claim ID.
    """
    try:
        updated_claim_model_inference = db.scalar(update_claim_model_inference_by_claim_id_query(claim_id, claim_model_inference_data))
        db.commit()
        return updated_claim_model_inference
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

def delete_claim_model_inference(db: Session, claim_model_inference_id: UUID) -> Optional[ClaimModelInference]:
    """
    Delete a claim model inference from the database by its ID.
    """
    try:
        deleted_claim_model_inference = db.scalar(delete_claim_model_inference_query(claim_model_inference_id))
        db.commit()
        return deleted_claim_model_inference
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

## Claim Detection Model CRUD Operations
def get_claim_detection_model_by_id(db: Session, claim_detection_model_id: UUID) -> Optional[ClaimDetectionModel]:
    """
    Retrieve a claim detection model from the database by its ID.
    """
    try:
        return db.scalar(get_claim_detection_model_by_id_query(claim_detection_model_id))
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def get_claim_detection_model_by_name(db: Session, name: str) -> Optional[ClaimDetectionModel]:
    """
    Retrieve a claim detection model from the database by its name.
    """
    try:
        return db.scalar(get_claim_detection_model_by_name_query(name))
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def insert_claim_detection_model(db: Session, claim_detection_model_data: dict) -> Optional[ClaimDetectionModel]:
    """
    Insert a claim detection model into the database.
    """
    try:
        return db.scalar(insert_claim_detection_model_query(claim_detection_model_data))
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def update_claim_detection_model(db: Session, claim_detection_model_id: UUID, claim_detection_model_data: dict) -> Optional[ClaimDetectionModel]:
    """
    Update a claim detection model in the database by its ID.
    """
    try:
        updated_claim_detection_model = db.scalar(update_claim_detection_model_query(claim_detection_model_id, claim_detection_model_data))
        db.commit()
        return updated_claim_detection_model
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

def delete_claim_detection_model(db: Session, claim_detection_model_id: UUID) -> Optional[ClaimDetectionModel]:
    """
    Delete a claim detection model from the database by its ID.
    """
    try:
        deleted_claim_detection_model = db.scalar(delete_claim_detection_model_query(claim_detection_model_id))
        db.commit()
        return deleted_claim_detection_model
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

## Annotation Session CRUD Operations
def get_annotation_session_by_id(db: Session, annotation_session_id: UUID) -> Optional[AnnotationSession]:
    """
    Retrieve an annotation session from the database by its ID.
    """
    try:
        return db.scalar(get_annotation_session_by_id_query(annotation_session_id))
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def insert_annotation_session(db: Session) -> Optional[UUID]:
    """
    Insert an annotation session into the database.
    """
    try:
        inserted_annotation_session = db.scalar(insert_annotation_session_query())
        return inserted_annotation_session
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def update_annotation_session(db: Session, annotation_session_id: UUID, annotation_session_data: dict) -> Optional[AnnotationSession]:
    """
    Update an annotation session in the database by its ID.
    """
    try:
        updated_annotation_session = db.scalar(update_annotation_session_query(annotation_session_id, annotation_session_data))
        db.commit()
        return updated_annotation_session
    except Exception as e:
        traceback.print_exc()
        db.rollback()       
        raise Exception(f"{str(e)}")

def delete_annotation_session(db: Session, annotation_session_id: UUID) -> Optional[AnnotationSession]:
    """
    Delete an annotation session from the database by its ID.
    """
    try:
        deleted_annotation_session = db.scalar(delete_annotation_session_query(annotation_session_id))
        db.commit()
        return deleted_annotation_session
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

## Claim Annotation CRUD Operations
def get_claim_annotation_by_claim_id(db: Session, claim_id: UUID) -> Optional[ClaimAnnotation]:
    """
    Retrieve a claim annotation from the database by its claim ID.
    """
    try:
        return db.scalar(get_claim_annotation_by_claim_id_query(claim_id))
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def get_claim_annotation_by_source_document_id(db: Session, source_document_id: UUID) -> Optional[List[ClaimAnnotation]]:
    """
    Retrieve a claim annotation from the database by its source document ID.
    """
    try:
        return db.scalars(get_claim_annotation_by_source_document_id_query(source_document_id)).all()
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def get_claim_annotation_by_annotation_session_id(db: Session, annotation_session_id: UUID) -> Optional[List[ClaimAnnotation]]:
    """
    Retrieve a claim annotation from the database by its annotation session ID.
    """
    try:
        return db.scalars(get_claim_annotation_by_annotation_session_id_query(annotation_session_id)).all()
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def insert_claim_annotation(db: Session, claim_annotation_data: List[dict]) -> Optional[List[ClaimAnnotation]]:
    """
    Insert a claim annotation into the database.
    """
    try:
        inserted_claim_annotation = db.scalars(insert_claim_annotation_query(claim_annotation_data)).all()
        return inserted_claim_annotation
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"FAILED to insert claim annotation into the database: {str(e)}")
    
def update_claim_annotation(db: Session, annotation_session_id: UUID, claim_id: UUID, claim_annotation_data: dict) -> Optional[ClaimAnnotation]:
    """
    Update a claim annotation in the database by its ID.
    """
    try:
        updated_claim_annotation = db.scalar(update_claim_annotation_query(annotation_session_id, claim_id, claim_annotation_data))
        return updated_claim_annotation
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def delete_claim_annotation(db: Session, annotation_session_id: UUID, claim_id: UUID) -> Optional[ClaimAnnotation]:
    """
    Delete a claim annotation from the database by its ID.
    """
    try:
        deleted_claim_annotation = db.scalar(delete_claim_annotation_query(annotation_session_id, claim_id))
        db.commit()
        return deleted_claim_annotation
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

## Claim with Inference and Annotation Queries
def get_claims_with_inference_and_annotation(db: Session, start_date: datetime, end_date: datetime):
    """
    Retrieve claims with their model inferences and annotations within a time range.
    """
    try:
        query = get_claims_with_inference_and_annotation_query(start_date, end_date)    
        results = db.execute(query).all()
        return results
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")