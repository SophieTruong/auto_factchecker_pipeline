"""
Database Models Module

This module defines SQLAlchemy ORM models for interacting with a PostgreSQL database.
"""
from sqlalchemy import Column, LargeBinary

from .postgres import Base

class APIKey(Base):
    """
    Represents an API key in the database.
    """
    __tablename__ = 'api_key'
    
    hashed_api_key = Column(LargeBinary, nullable=False, primary_key=True)