from typing import List, Optional
from datetime import datetime
import traceback

from sqlalchemy.orm import Session

from .models import Claim
from .queries import (
    get_claim_by_id_query, 
    get_claim_by_text_query, 
    get_claims_by_time_range_query, 
    insert_claims_query,
    update_claim_query,
    delete_claim_query
)

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
    
    if not db:
        raise ValueError("Database session cannot be None")
    
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
    if not db:
        raise ValueError("Database session cannot be None")
    
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
    if not db:
        raise ValueError("Database session cannot be None")
        
    if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
        raise ValueError("start_date and end_date must be datetime objects")
        
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
    if not db:
        raise ValueError("Database session cannot be None")
    
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
    if not db:
        raise ValueError("Database session cannot be None")
        
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
    if not db:
        raise ValueError("Database session cannot be None")
        
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
    
