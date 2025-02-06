from pydantic import BaseModel, ConfigDict

from typing import Optional, List
from uuid import UUID

class SemanticSearchInput(BaseModel):
    """
    Input model for the claim detection service.
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    claims: List[str]
