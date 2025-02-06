from pydantic import BaseModel, Field
from datetime import datetime, timezone

class InferenceResult(BaseModel):
    """
    Model inference result.
    """
    label: bool = Field(description="The label of the claim")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="The timestamp of the inference")
    
    
class ModelMetadata(BaseModel):
    """
    Model metadata.
    """
    model_name: str = Field(description="The name of the model")
    model_version: str = Field(description="The version of the model")
    model_path: str = Field(description="The path to the model")
    created_at: datetime = Field(description="The timestamp of the model creation")
