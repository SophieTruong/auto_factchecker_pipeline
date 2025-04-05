from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .utils import get_utcnow

class SourceDocumentBase(BaseModel):
    """
    Input model for the claim detection service.
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    text: str = Field(min_length=1, description="The text of the claim")

class SourceDocumentCreate(SourceDocumentBase):
    """
    Input model for creating a source document.
    """
    pass

class SourceDocument(SourceDocumentBase):
    """
    Model representing a stored source document with metadata.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime = Field(default_factory=get_utcnow, description="Timestamp of creation")
    updated_at: datetime = Field(default_factory=get_utcnow, description="Timestamp of last update")


