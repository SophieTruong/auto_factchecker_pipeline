from pydantic import BaseModel
from typing import Optional, List
class SearchInput(BaseModel):
    claims: List[str]

class SingleClaimSearchResult(BaseModel):
    id: int
    distance: float
    source: str
    timestamp: str
    text: str
    label: Optional[str] = None

class ClaimSearchResult(BaseModel):
    claim: str
    results: Optional[List[SingleClaimSearchResult]]

class SearchResponse(BaseModel):
    claims: List[ClaimSearchResult]
    