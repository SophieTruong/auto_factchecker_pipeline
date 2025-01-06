from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class ClaimBase(BaseModel):
    """
    Pydantic Base model for the claim object.
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    text: str = Field(min_length=1, description="The text of the claim")
    label: bool = Field(description="The label of the claim")
    
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

    id: int
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of creation")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of last update")
