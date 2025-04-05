from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from .utils import get_utcnow

class ClaimBase(BaseModel):
    """
    Pydantic Base model for the claim object.
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    text: str = Field(min_length=0, description="The text of the claim")
    source_document_id: UUID = Field(description="The ID of the source document")
    
class ClaimCreate(ClaimBase):
    """
    Pydantic model for creating a claim.
    """
    pass

class Claim(ClaimBase):
    """
    Model representing a stored claim with metadata.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime = Field(default_factory=get_utcnow, description="Timestamp of creation")
    updated_at: datetime = Field(default_factory=get_utcnow, description="Timestamp of last update")
