import sys

print(f"*** sys.path: {sys.path}")

from typing import Optional
from utils.password_hashing import hash_password
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


def reset_api_keys(db: Session) -> None:
    """
    Remove all API keys from the database.
    """
    try:
        db.query(APIKey).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise Exception(f"Failed to reset API keys: {str(e)}")


def remove_api_key(db: Session, key: str) -> None:
    """
    Remove a specific API key from the database by its hashed key.
    """
    try:
        api_key = (
            db.query(APIKey).filter(APIKey.hashed_api_key == hash_password(key)).first()
        )
        if api_key:
            db.delete(api_key)
            db.commit()
        else:
            raise Exception("API key not found.")
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise Exception(f"Failed to remove API key: {str(e)}")


def add_api_key(db: Session, raw_key: str) -> APIKey:
    """
    Add a new API key to the database after hashing it.
    """
    try:
        hashed_key = hash_password(raw_key)
        new_api_key = APIKey(hashed_api_key=hashed_key)
        db.add(new_api_key)
        db.commit()
        db.refresh(new_api_key)
        return new_api_key
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise Exception(f"Failed to add API key: {str(e)}")
