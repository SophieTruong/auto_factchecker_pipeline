from typing import Optional
from datetime import datetime

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
    try:
        parsed_start = datetime.strptime(start_date.strip(), "%Y-%m-%d")
        parsed_end = datetime.strptime(end_date.strip(), "%Y-%m-%d")
        return parsed_start, parsed_end
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")
    
