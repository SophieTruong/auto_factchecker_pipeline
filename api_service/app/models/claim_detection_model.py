from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class ClaimDetectionModel(BaseModel):
    """
    Base model for the claim detection model.
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, description="The name of pre-trained model family")
    version: str = Field(min_length=1, description="The version of the claim detection model")
    model_path: str = Field(min_length=1, description="The path to the claim detection model")
    created_at: datetime = Field(description="Timestamp of creation")