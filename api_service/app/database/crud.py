from typing import List, Optional
from datetime import datetime
import traceback

from sqlalchemy.orm import Session

from .models import (
    Claim, SourceDocument, 
    ClaimModelInference, 
    ClaimDetectionModel, 
    ClaimAnnotation
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
    delete_claim_query,
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
    update_claim_detection_model_query,
    delete_claim_detection_model_query,
    # Claim Annotation Queries
    insert_claim_annotation_query,
    get_claim_annotation_by_id_query,
    get_claim_annotation_by_source_document_id_query,
    update_claim_annotation_query,
    delete_claim_annotation_query,
)

## Source Document CRUD Operations
def get_source_document_by_id(db: Session, source_document_id: int) -> Optional[SourceDocument]:
    """
    Retrieve a source document from the database by its ID.
    """
    if not isinstance(source_document_id, int) or source_document_id <= 0:
        raise ValueError("source_document_id must be a positive integer")
    
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
        existing_source_document = get_source_document_by_text(db, source_document_data['text'])
        if existing_source_document:
            raise ValueError("Source document already exists in the database")
        inserted_source_document = db.scalar(insert_source_document_query(source_document_data))
        db.commit()
        return inserted_source_document
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

def update_source_document(db: Session, source_document_id: int, source_document_data: dict) -> Optional[SourceDocument]:
    """
    Update a source document in the database by its ID.
    """
    if not isinstance(source_document_id, int) or source_document_id <= 0:
        raise ValueError("source_document_id must be a positive integer")

    try:
        updated_source_document = db.scalar(update_source_document_query(source_document_id, source_document_data))
        db.commit()
        return updated_source_document
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

def delete_source_document(db: Session, source_document_id: int) -> Optional[SourceDocument]:
    """
    Delete a source document from the database by its ID.
    """
    if not isinstance(source_document_id, int) or source_document_id <= 0:
        raise ValueError("source_document_id must be a positive integer")
    
    try:
        deleted_source_document = db.scalar(delete_source_document_query(source_document_id))
        db.commit()
        return deleted_source_document
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")


## Claim CRUD Operations
def get_claim_by_id(db: Session, claim_id:int) -> Optional[Claim]:
    """
    Retrieve a claim from the database by its ID.

    Args:
        db (Session): Database session
        claim_id (int): ID of the claim to retrieve

    Returns:
        Optional[Claim]: The claim if found, None otherwise
    """
    if not isinstance(claim_id, int) or claim_id <= 0:
        raise ValueError("claim_id must be a positive integer")
        
    try:
        return db.scalar(get_claim_by_id_query(claim_id))
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def get_claims_by_text(db: Session, text: str) -> Optional[List[Claim]]:
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
        return db.scalars(query)
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
        return db.scalars(get_claims_by_time_range_query(start_date, end_date))
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
    tobe_inserted = []       
    
    try:
        # Check if claim already exists
        for claim in claims_data:
            existing_claim = get_claims_by_text(db, claim['text'])
            if not existing_claim:
                tobe_inserted.append(claim)
        
        # Bulk insert claims that are not already in the database and return inserted claims.
        if len(tobe_inserted) > 0:
            inserted_claims = db.scalars(insert_claims_query(tobe_inserted))
            db.commit()
            return inserted_claims
        
        else:
            raise ValueError("All claims are already in the database. No claims inserted.")
    
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")
    
def update_claim(db: Session, claim_id: int, claim_data: dict) -> Optional[Claim]:
    """
    Update a claim in the database by its ID.
    """        
    if not isinstance(claim_id, int) or claim_id <= 0:
        raise ValueError("claim_id must be a positive integer")
        
    if not claim_data or not isinstance(claim_data, dict):
        raise ValueError("claim_data must be a non-empty dictionary")

    try:
        updated_claim = db.scalar(update_claim_query(claim_id, claim_data))
        db.commit()
        return updated_claim
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"db.scalar fails: {str(e)}")

def delete_claim(db: Session, claim_id: int) -> Optional[int]:
    """
    Delete a claim from the database by its ID.
    """        
    if not isinstance(claim_id, int) or claim_id <= 0:
        raise ValueError("claim_id must be a positive integer")
    
    try:
        deleted_claim = db.scalar(delete_claim_query(claim_id))
        db.commit()
        return deleted_claim
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")
    

## Claim Model Inference CRUD Operations
def get_claim_model_inference_by_id(db: Session, claim_model_inference_id: int) -> Optional[ClaimModelInference]:
    """x
    Retrieve a claim model inference from the database by its ID.
    """
    if not isinstance(claim_model_inference_id, int) or claim_model_inference_id <= 0:
        raise ValueError("claim_model_inference_id must be a positive integer")

    try:
        return db.scalar(get_claim_model_inference_by_id_query(claim_model_inference_id))
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def get_claim_model_inference_by_claim_id(db: Session, claim_id: int) -> Optional[ClaimModelInference]:
    """
    Retrieve a claim model inference from the database by its claim ID.
    """
    if not isinstance(claim_id, int) or claim_id <= 0:
        raise ValueError("claim_id must be a positive integer")

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
        inserted_claim_model_inference = db.scalars(insert_claim_model_inference_query(claim_model_inference_data))
        db.commit()
        return inserted_claim_model_inference
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

def update_claim_model_inference(db: Session, claim_model_inference_id: int, claim_model_inference_data: dict) -> Optional[ClaimModelInference]:
    """
    Update a claim model inference in the database by its ID.
    """
    if not isinstance(claim_model_inference_id, int) or claim_model_inference_id <= 0:
        raise ValueError("claim_model_inference_id must be a positive integer")

    try:
        updated_claim_model_inference = db.scalar(update_claim_model_inference_query(claim_model_inference_id, claim_model_inference_data))
        db.commit()
        return updated_claim_model_inference
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

def update_claim_model_inference_by_claim_id(db: Session, claim_id: int, claim_model_inference_data: dict) -> Optional[ClaimModelInference]:
    """
    Update a claim model inference in the database by its claim ID.
    """
    if not isinstance(claim_id, int) or claim_id <= 0:
        raise ValueError("claim_id must be a positive integer")

    try:
        updated_claim_model_inference = db.scalar(update_claim_model_inference_by_claim_id_query(claim_id, claim_model_inference_data))
        db.commit()
        return updated_claim_model_inference
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

def delete_claim_model_inference(db: Session, claim_model_inference_id: int) -> Optional[ClaimModelInference]:
    """
    Delete a claim model inference from the database by its ID.
    """
    if not isinstance(claim_model_inference_id, int) or claim_model_inference_id <= 0:
        raise ValueError("claim_model_inference_id must be a positive integer") 
    
    try:
        deleted_claim_model_inference = db.scalar(delete_claim_model_inference_query(claim_model_inference_id))
        db.commit()
        return deleted_claim_model_inference
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

## Claim Detection Model CRUD Operations
def get_claim_detection_model_by_id(db: Session, claim_detection_model_id: int) -> Optional[ClaimDetectionModel]:
    """
    Retrieve a claim detection model from the database by its ID.
    """
    if not isinstance(claim_detection_model_id, int) or claim_detection_model_id <= 0:
        raise ValueError("claim_detection_model_id must be a positive integer")
    
    try:
        return db.scalar(get_claim_detection_model_by_id_query(claim_detection_model_id))
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def insert_claim_detection_model(db: Session, claim_detection_model_data: dict) -> Optional[ClaimDetectionModel]:
    """
    Insert a claim detection model into the database.
    """
    try:
        inserted_claim_detection_model = db.scalar(insert_claim_detection_model_query(claim_detection_model_data))
        db.commit()
        return inserted_claim_detection_model
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

def update_claim_detection_model(db: Session, claim_detection_model_id: int, claim_detection_model_data: dict) -> Optional[ClaimDetectionModel]:
    """
    Update a claim detection model in the database by its ID.
    """
    if not isinstance(claim_detection_model_id, int) or claim_detection_model_id <= 0:
        raise ValueError("claim_detection_model_id must be a positive integer")

    try:
        updated_claim_detection_model = db.scalar(update_claim_detection_model_query(claim_detection_model_id, claim_detection_model_data))
        db.commit()
        return updated_claim_detection_model
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

def delete_claim_detection_model(db: Session, claim_detection_model_id: int) -> Optional[ClaimDetectionModel]:
    """
    Delete a claim detection model from the database by its ID.
    """
    if not isinstance(claim_detection_model_id, int) or claim_detection_model_id <= 0:
        raise ValueError("claim_detection_model_id must be a positive integer")
    
    try:
        deleted_claim_detection_model = db.scalar(delete_claim_detection_model_query(claim_detection_model_id))
        db.commit()
        return deleted_claim_detection_model
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")


## Claim Annotation CRUD Operations
def get_claim_annotation_by_id(db: Session, claim_annotation_id: int) -> Optional[ClaimAnnotation]:
    """
    Retrieve a claim annotation from the database by its ID.
    """
    if not isinstance(claim_annotation_id, int) or claim_annotation_id <= 0:
        raise ValueError("claim_annotation_id must be a positive integer")
    
    try:
        return db.scalar(get_claim_annotation_by_id_query(claim_annotation_id))
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def get_claim_annotation_by_source_document_id(db: Session, source_document_id: int) -> Optional[List[ClaimAnnotation]]:
    """
    Retrieve a claim annotation from the database by its source document ID.
    """
    if not isinstance(source_document_id, int) or source_document_id <= 0:
        raise ValueError("source_document_id must be a positive integer")

    try:
        return db.scalars(get_claim_annotation_by_source_document_id_query(source_document_id))
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")

def insert_claim_annotation(db: Session, claim_annotation_data: List[dict]) -> Optional[List[ClaimAnnotation]]:
    """
    Insert a claim annotation into the database.
    """
    try:
        inserted_claim_annotation = db.scalars(insert_claim_annotation_query(claim_annotation_data))
        db.commit()
        return inserted_claim_annotation
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")
    
def update_claim_annotation(db: Session, claim_annotation_id: int, claim_annotation_data: dict) -> Optional[ClaimAnnotation]:
    """
    Update a claim annotation in the database by its ID.
    """
    if not isinstance(claim_annotation_id, int) or claim_annotation_id <= 0:
        raise ValueError("claim_annotation_id must be a positive integer")

    try:
        updated_claim_annotation = db.scalar(update_claim_annotation_query(claim_annotation_id, claim_annotation_data))
        db.commit()
        return updated_claim_annotation
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")

def delete_claim_annotation(db: Session, claim_annotation_id: int) -> Optional[ClaimAnnotation]:
    """
    Delete a claim annotation from the database by its ID.
    """
    if not isinstance(claim_annotation_id, int) or claim_annotation_id <= 0:
        raise ValueError("claim_annotation_id must be a positive integer")

    try:
        deleted_claim_annotation = db.scalar(delete_claim_annotation_query(claim_annotation_id))
        db.commit()
        return deleted_claim_annotation
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise Exception(f"{str(e)}")
