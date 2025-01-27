from pydantic import BaseModel, ConfigDict, Field

from typing import Optional, List
from uuid import UUID

# TODO: let make this a list
class SemanticSearchInput(BaseModel):
    """
    Input model for the claim detection service.
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    claim: str = Field(min_length=1, description="The text of the claim")


# TODO: move this to its own file
class SemanticSearchResult(BaseModel):
    pass
class SemanticSearchResponse(BaseModel):
    claim_id: UUID
    claim_text: str
    search_result: Optional[List[SemanticSearchResult]]

class BatchSemanticSearchResponse(BaseModel):
    batch_response: List[SemanticSearchResponse]