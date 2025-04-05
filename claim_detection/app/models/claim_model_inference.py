from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .utils import get_utcnow

class ClaimModelInferenceBase(BaseModel):
    """
    Base model for the claim model inference.
    """
    claim_id: UUID = Field(description="The ID of the claim")
    claim_detection_model_id: UUID = Field(description="The ID of the claim detection model")
    label: bool = Field(description="The label of the claim")

class ClaimModelInferenceCreate(ClaimModelInferenceBase):
    """
    Input model for creating a claim model inference.
    """
    pass

class ClaimModelInference(ClaimModelInferenceBase):
    """
    Model representing a stored claim model inference with metadata.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime = Field(default_factory=get_utcnow, description="Timestamp of creation")
    updated_at: datetime = Field(default_factory=get_utcnow, description="Timestamp of last update")

