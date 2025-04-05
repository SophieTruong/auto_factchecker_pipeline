from datetime import datetime, timezone

def get_utcnow():
    """
    Get the current UTC timestamp.
    """
    return datetime.now(timezone.utc)