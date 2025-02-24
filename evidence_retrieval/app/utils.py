from datetime import datetime
from typing import List

def validate_and_fix_date(date_str: str, claim_index: int) -> datetime:
    """
    Validates a date string and returns current date if invalid.
    Args:
        date_str: Date string in YYYY-MM-DD format
        claim_index: Index of the claim for logging
    Returns:
        Valid date string in YYYY-MM-DD format
    """
    current_date = datetime.now()
    
    # Check for empty date
    if not date_str:
        print(f"No date found for claim {claim_index}")
        return current_date
    
    try:
        # Convert to date object and validate
        check_date = datetime.strptime(date_str, "%Y-%m-%d")
        if check_date > datetime.now():
            print(f"Date {date_str} is in the future for claim {claim_index}")
            return current_date
        return check_date
        
    except ValueError:
        print(f"Invalid date format for claim {claim_index}")
        return current_date

def process_factcheck_dates(factcheck_dates: List[str]) -> List[str]:
    """
    Process and validate a list of factcheck dates.
    Returns list with invalid dates replaced by current date.
    """
    return [
        validate_and_fix_date(date, i) 
        for i, date in enumerate(factcheck_dates)
    ]