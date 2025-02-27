from typing import Dict, List, Union
from pydantic import BaseModel
from factchecked_data import PoliticFactData, FaktaBaari, FactCheckOrg, FullFact, Snopes

# Define a union type for all possible fact-check types
FactCheckResult = Union[PoliticFactData, FaktaBaari, FactCheckOrg, FullFact, Snopes]

# Define the response type
SourceSearchResults = Dict[str, List[FactCheckResult]]

class Claim(BaseModel):
    claim: str
    timestamp: str

class SearchInput(BaseModel):
    claims: List[Claim]

class SingleSearchResult(BaseModel):
    claim: str
    response: SourceSearchResults

class SearchResponse(BaseModel):
    results: List[SingleSearchResult]