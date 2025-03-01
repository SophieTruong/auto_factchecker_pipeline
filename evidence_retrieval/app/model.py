from pydantic import BaseModel
from typing import Optional, List

class Claim(BaseModel):
    claim: str
    timestamp: Optional[str] = None
    
class SearchInput(BaseModel):
    claims: List[Claim]

class SingleClaimSearchResult(BaseModel):
    id: int
    distance: float
    source: str
    timestamp: str | int
    text: str
    label: Optional[str] = None
    url: Optional[str] = None

class ClaimSearchResult(BaseModel):
    claim: str
    vector_db_results: Optional[List[SingleClaimSearchResult]]
    web_search_results: Optional[dict]
    
class SearchResponse(BaseModel):
    claims: List[ClaimSearchResult]
    