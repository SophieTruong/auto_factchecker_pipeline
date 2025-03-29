"""
Database Models Module

This module defines SQLAlchemy ORM models for interacting with a PostgreSQL database.
"""
from sqlalchemy import Column, Index, Boolean, String, ForeignKey, Boolean, UUID, UniqueConstraint, LargeBinary
from sqlalchemy.dialects.postgresql import UUID, TEXT
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

import uuid

from .postgres import Base
from .utils import utcnow, cast_language_literal

class APIKey(Base):
    """
    Represents an API key in the database.
    """
    __tablename__ = 'api_key'
    
    hashed_api_key = Column(LargeBinary, nullable=False, primary_key=True)
    
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
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(TEXT, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=utcnow(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=utcnow(), onupdate=utcnow(), nullable=False)
    
    # Add index on text column
    __table_args__ = (
        Index('ix_source_document_text_hash', func.md5(text), unique=True),
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
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(String, nullable=False)
    source_document_id = Column(UUID(as_uuid=True), ForeignKey('source_document.id')) #https://stackoverflow.com/questions/77587206/is-that-possible-to-define-set-null-for-only-one-column-of-composite-foreign-k
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
        UniqueConstraint('text', name='uq_claim_text'),
    )
    
class ClaimModelInference(Base, StringRepresentation):
    """
    Represents a claim model inference in the database.
    """
    __tablename__ = 'claim_model_inference'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey('claim.id', ondelete='CASCADE'))
    claim_detection_model_id = Column(UUID(as_uuid=True), ForeignKey('claim_detection_model.id'))
    label = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=utcnow(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=utcnow(), onupdate=utcnow(), nullable=False)

    __table_args__ = (
        UniqueConstraint('claim_id', 'claim_detection_model_id', name='uq_claim_model_inference_claim_model'),
    )

class ClaimDetectionModel(Base, StringRepresentation):
    """
    Represents a model in the database.
    """
    __tablename__ = 'claim_detection_model'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    model_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=utcnow(), nullable=False)

class AnnotationSession(Base, StringRepresentation):
    """
    Represents an annotation session in the database.
    """
    __tablename__ = 'annotation_session'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=utcnow(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=utcnow(), onupdate=utcnow(), nullable=False)

class ClaimAnnotation(Base, StringRepresentation):
    """
    Represents a claim annotation in the database.
    """
    __tablename__ = 'claim_annotation'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_document_id = Column(UUID(as_uuid=True), ForeignKey('source_document.id'))
    claim_id = Column(UUID(as_uuid=True), ForeignKey('claim.id', ondelete='CASCADE'))
    annotation_session_id = Column(UUID(as_uuid=True), ForeignKey('annotation_session.id', ondelete='CASCADE'))
    binary_label = Column(Boolean, nullable=False)
    text_label = Column(String, nullable=True)
    
    __table_args__ = (
        UniqueConstraint('claim_id', 'annotation_session_id', name='uq_claim_annotation_session'),
    )