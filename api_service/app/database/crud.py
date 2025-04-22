import sys
print(f"*** sys.path: {sys.path}")

from typing import Optional
import traceback

from sqlalchemy.orm import Session

from .models import APIKey
## API Key CRUD Operations
def get_all_api_keys(db: Session) -> Optional[APIKey]:
    """
    Retrieve an API key from the database by its hashed API key.
    """
    try:
        return db.query(APIKey).all()
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"{str(e)}")