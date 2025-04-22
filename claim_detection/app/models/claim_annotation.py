from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class ClaimAnnotationBase(BaseModel):
    """
    Input model for the claim detection service.
    """
    source_document_id: UUID = Field(description="The ID of the source document")
    claim_id: UUID = Field(description="The ID of the claim")
    annotation_session_id: UUID = Field(description="The ID of the annotation session")
    binary_label: bool = Field(description="The binary label of the claim")
    text_label: str | None = Field(description="The text label of the claim")

class ClaimAnnotationCreate(ClaimAnnotationBase):
    """
    Input model for creating a claim annotation.
    """
    pass
class ClaimAnnotation(ClaimAnnotationBase):
    """
    Model representing a stored claim annotation with metadata.
    """
    model_config = ConfigDict(from_attributes=True)
    id: UUID
