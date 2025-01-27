from fastapi import HTTPException

from typing import Optional
from datetime import datetime

def validate_claim_id(claim_id: Optional[str]) -> int:
    """
    Validate the claim ID.
    
    Args:
        claim_id (Optional[str]): Input claim ID
    
    Returns:
        int: Validated claim ID
    
    Raises:
        HTTPException: If the claim ID is empty or fails to validate
    """
    try:
        return int(claim_id.strip())
    except ValueError:
        raise HTTPException(status_code=400, detail="Claim ID must be a valid integer")

def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> tuple[datetime, datetime]:
    """
    Validate the date range.
    
    Args:
        start_date (Optional[str]): Start date
        end_date (Optional[str]): End date
    
    Returns:
        tuple[datetime, datetime]: Validated date range
    
    Raises:
        HTTPException: If the date range is empty or fails to validate
    """
    # Validate start_date and end_date
    if not start_date or not start_date.strip():
        raise HTTPException(status_code=400, detail="Start date cannot be empty")
    if not end_date or not end_date.strip():
        raise HTTPException(status_code=400, detail="End date cannot be empty")

    try:
        parsed_start = datetime.strptime(start_date.strip(), "%Y-%m-%d")
        parsed_end = datetime.strptime(end_date.strip(), "%Y-%m-%d")
        return parsed_start, parsed_end
    except ValueError:
        raise HTTPException(status_code=400, detail="Dates must be in YYYY-MM-DD format")
    
