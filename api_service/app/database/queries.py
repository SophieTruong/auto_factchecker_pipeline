from datetime import datetime
from typing import List

from sqlalchemy import select, insert, update, delete
from sqlalchemy.sql import func

from .models import Claim
from .utils import cast_language_literal, sanitize_string

def get_claim_by_id_query(claim_id: int):
    """
    Create a query for a claim by its ID
    """
    return select(Claim).where(Claim.id == claim_id)

def get_claims_by_time_range_query(start_date: datetime, end_date: datetime):
    """
    Create a query for claims by their creation date range
    """
    return select(Claim).where(Claim.created_at >= start_date, Claim.created_at <= end_date)

def get_claim_by_text_query(text: str):
    """
    Create a text search query for claims
    """
    sanitized_text = sanitize_string(text)
    
    return select(Claim).where(
        func.to_tsvector(
            cast_language_literal("finnish"),
            Claim.text
        ).bool_op("@@")(
            func.websearch_to_tsquery(
                cast_language_literal("finnish"),
                sanitized_text
            )
        )
    )

def insert_claims_query(claims_data: List[dict]):
    """
    Create a query for inserting claims
    """
    return insert(Claim).values(claims_data).returning(Claim)

def update_claim_query(claim_id: int, claim_data: dict):
    """
    Create a query for updating a claim
    """
    return update(Claim).where(Claim.id == claim_id).values(claim_data).returning(Claim)

def delete_claim_query(claim_id: int):
    """
    Create a query for deleting a claim
    """
    return delete(Claim).where(Claim.id == claim_id).returning(Claim)