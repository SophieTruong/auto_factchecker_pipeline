from pydantic import BaseModel, ConfigDict, Field

from typing import Optional, List
from uuid import UUID

class SemanticSearchInput(BaseModel):
    """
    Input model for the claim detection service.
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    claim: str = Field(min_length=1, max_length=200)
    timestamp: Optional[str] = None

class SemanticSearchInputs(BaseModel):
    """
    Input model for the claim detection service.
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    claims: List[SemanticSearchInput]
