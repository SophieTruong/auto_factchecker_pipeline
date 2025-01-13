"""
Database Models Module

This module defines SQLAlchemy ORM models for interacting with a PostgreSQL database.
"""
from sqlalchemy import Column, Index, Integer, String, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from .postgres import Base
from .utils import utcnow, cast_language_literal

class StringRepresentation:
    """
    Base class for string representation of models
    """
    def __str__(self) -> str:
        """
        Returns a string representation of the model
        """
        return '\n'.join(
            f'{column.name}: {getattr(self, column.name)}'
            for column in self.__table__.columns
        )

class SourceDocument(Base, StringRepresentation):
    """
    Represents a source document for claim detection model in the database.
    """
    __tablename__ = 'source_document'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=utcnow(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=utcnow(), onupdate=utcnow(), nullable=False)
    
    # Add index on text column
    __table_args__ = (
        Index('idx_source_document_text_unique', func.to_tsvector(cast_language_literal("finnish"), text), postgresql_using='gin'),
    )

class Claim(Base, StringRepresentation):
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
    source_document_id = Column(Integer, ForeignKey('source_document.id')) #https://stackoverflow.com/questions/77587206/is-that-possible-to-define-set-null-for-only-one-column-of-composite-foreign-k
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
    __table_args__ = (
        Index('idx_claim_text_unique', func.to_tsvector(cast_language_literal("finnish"), text), postgresql_using='gin'),
    )
    
class ClaimModelInference(Base, StringRepresentation):
    """
    Represents a claim model inference in the database.
    """
    __tablename__ = 'claim_model_inference'

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(Integer, ForeignKey('claim.id'))
    claim_detection_model_id = Column(Integer, ForeignKey('claim_detection_model.id'))
    label = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=utcnow(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=utcnow(), onupdate=utcnow(), nullable=False)

class ClaimDetectionModel(Base, StringRepresentation):
    """
    Represents a model in the database.
    """
    __tablename__ = 'model'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    model_path = Column(String, nullable=False)

class ClaimAnnotation(Base, StringRepresentation):
    """
    Represents a claim annotation in the database.
    """
    __tablename__ = 'claim_annotation'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_document_id = Column(Integer, ForeignKey('source_document.id'))
    claim_id = Column(Integer, ForeignKey('claim.id'))
    binary_label = Column(Boolean, nullable=False)
    text_label = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=utcnow(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=utcnow(), onupdate=utcnow(), nullable=False)
