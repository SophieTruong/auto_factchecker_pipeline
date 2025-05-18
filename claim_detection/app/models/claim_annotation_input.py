from typing import List
from uuid import UUID

from pydantic import BaseModel, Field

class ClaimAnnotationInput(BaseModel):
    """
    Input model for claim annotation.
    """
    source_document_id: UUID = Field(description="The ID of the source document")
    claim_id: UUID = Field(description="The ID of the claim")
    claim_text: str = Field(description="The text of the claim")
    binary_label: bool = Field(description="The binary label of the claim")
    text_label: str | None = Field(description="The text label of the claim")

class BatchClaimAnnotationInput(BaseModel):
    """
    Input model for batch claim annotation.
    """
    claims: List[ClaimAnnotationInput]
