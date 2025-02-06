from typing import List, Optional

from models.semantic_search_input import SemanticSearchInput
from models.semantic_search_response import BatchSemanticSearchResponse

from utils.make_request import make_request
from utils.app_logging import logger  

class SemanticSearchService:
    def __init__(self, semantic_search_service_uri: str):
        self.semantic_search_service_uri = semantic_search_service_uri

    def get_search_result(self, claims: SemanticSearchInput):
        return self._process_predictions(claims)
    
    async def _process_predictions(self, claims: SemanticSearchInput) -> List[BatchSemanticSearchResponse]:
        """Get and store model predictions for claims."""
        # Get model predictions
        search_results = await make_request(self.semantic_search_service_uri, claims.model_dump())        
        return search_results
    
    def _correct_str_format(self, txt):
        txt = txt.replace("\'", "\"")
        return txt
    
