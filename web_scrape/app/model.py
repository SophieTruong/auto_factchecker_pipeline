from typing import Dict, List, Union
from pydantic import BaseModel
from factchecked_data import PoliticFactData, FaktaBaari, FactCheckOrg, FullFact

# Define a union type for all possible fact-check types
FactCheckResult = Union[PoliticFactData, FaktaBaari, FactCheckOrg, FullFact]

# Define the response type
SourceSearchResults = Dict[str, List[FactCheckResult]]

class SearchInput(BaseModel):
    claims: List[str]

class SingleSearchResult(BaseModel):
    claim: str
    response: SourceSearchResults

class SearchResponse(BaseModel):
    results: List[SingleSearchResult]