from uuid import UUID
from datetime import datetime
import json

from pymilvus import utility

import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# StreamHandler for the console
stream_handler = logging.StreamHandler(sys.stdout)

log_formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")

logger.addHandler(stream_handler)

logger.info("Logger initialized")


def validate_and_mk_hybrid_date(date_str: str) -> int:
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
    
def get_date_from_hybrid_ts(hybrid_ts: int) -> str:
    return utility.hybridts_to_datetime(hybrid_ts).strftime("%Y-%m-%d")


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)