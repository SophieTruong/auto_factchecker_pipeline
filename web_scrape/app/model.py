from typing import Dict, List, Union
from pydantic import BaseModel
from factchecked_data import PoliticFactData, FaktaBaari, GoogleCustomSearchEngine

# Define a union type for all possible fact-check types
FactCheckResult = Union[PoliticFactData, FaktaBaari, GoogleCustomSearchEngine]

# Define the response type
SourceSearchResults = Dict[str, List[FactCheckResult]]

class Claim(BaseModel):
    claim: str
    timestamp: str

class WebScrapResult(BaseModel):
    claim: str
    response: SourceSearchResults
