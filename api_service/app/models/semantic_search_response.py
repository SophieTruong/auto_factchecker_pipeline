from pydantic import BaseModel
from typing import Optional, List

# TODO: Review this
class SemanticSearchResult(BaseModel):
    id: int
    distance: float
    text: str
    source: str
    url: str
    timestamp: str
    label: Optional[str]
    
class SemanticSearchResponse(BaseModel):
    claim_text: str
    search_result: Optional[List[SemanticSearchResult]]

class BatchSemanticSearchResponse(BaseModel):
    batch_response: List[SemanticSearchResponse]