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
    url: Optional[str] = None

class ClaimSearchResult(BaseModel):
    claim: str
    vector_db_results: Optional[List[SingleClaimSearchResult]]
    web_search_results: Optional[dict]
    
class SearchResponse(BaseModel):
    claims: List[ClaimSearchResult]
    