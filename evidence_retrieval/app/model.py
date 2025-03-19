from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
class Claim(BaseModel):
    claim: str
    timestamp: Optional[str] = None
    
class SingleClaimSearchResult(BaseModel):
    id: str
    score: float
    source: str
    created_at: str
    text: str
    label: Optional[str] = None
    url: Optional[str] = None

class ClaimSearchResult(BaseModel):
    claim: str
    vector_db_results: Optional[List[SingleClaimSearchResult]]
    web_search_results: Optional[List[dict]]
    
class SearchResponse(BaseModel):
    claims: List[ClaimSearchResult]
    