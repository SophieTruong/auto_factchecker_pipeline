"""
Database Models Module

This module defines SQLAlchemy ORM models for interacting with a PostgreSQL database.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, Index, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from .postgres import Base
from .utils import utcnow, cast_language_literal

class Claim(Base):
    """
    Represents a claim in the database.
    
    Attributes:
        id (int): Unique identifier for the claim
        text (str): The actual claim text
        label (str): Classification label for the claim
        created_at (datetime): Timestamp when the claim was created
        updated_at (datetime): Timestamp when the claim was last updated
    """
    
    __tablename__ = 'claim'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)
    label = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=utcnow(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=utcnow(),
        onupdate=utcnow(),
        nullable=False
    )

    # Add index on text column
    # TODO: Add partition on created_at column -> Test if it's faster
    __table_args__ = (
        Index('idx_claim_text_unique', func.to_tsvector(cast_language_literal("finnish"), text), postgresql_using='gin'),
    )
    
    def __str__(self) -> str:
        """
        Returns a string representation of the Claim object.
        
        Returns:
            str: A formatted string containing all column values
        """
        return '\n'.join(
            f'{column.name}: {getattr(self, column.name)}'
            for column in self.__table__.columns
        )