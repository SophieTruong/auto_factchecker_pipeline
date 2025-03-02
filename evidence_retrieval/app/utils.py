from datetime import datetime
from typing import List
from pymilvus import utility

def validate_and_fix_date(date_str: str) -> int:
    """
    Validates a date string and returns current date if invalid.
    Args:
        date_str: Date string in YYYY-MM-DD format
        claim_index: Index of the claim for logging
    Returns:
        Valid date string in YYYY-MM-DD format
    """
    current_date = utility.mkts_from_datetime(datetime.now())
    
    # Check for empty date
    if not date_str:
        return current_date
    
    try:
        # Convert to date object and validate
        check_date = datetime.strptime(date_str, "%Y-%m-%d")
        if check_date > datetime.now():
            return current_date
        return utility.mkts_from_datetime(check_date)
        
    except ValueError:
        return current_date