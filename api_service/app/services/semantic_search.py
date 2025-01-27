from typing import List, Optional

from models.semantic_search_input import SemanticSearchInput

from utils.make_request import make_request
from utils.app_logging import logger  

import json

class SemanticSearchService:
    def __init__(self, semantic_search_service_uri: str):
        self.semantic_search_service_uri = semantic_search_service_uri

    def get_search_result(self, claim: SemanticSearchInput):
        return self._process_predictions(claim.model_dump())
    
    async def _process_predictions(self, claim: dict) -> List[dict]:
        """Get and store model predictions for claims."""
        # Get model predictions
        search_results = await make_request(self.semantic_search_service_uri, claim)
        
        logger.info(f"Semantic search search_results: {search_results}")
        
        search_result_lst = [*search_results.values()]
        
        ret = {}
        
        for i, ret_i in enumerate(search_result_lst):
            result_json = json.loads(self._correct_str_format(ret_i))
            logger.info(f"result_json: {result_json}")
            ret[i] = result_json
        
        logger.info(f"ret: {ret}")
        
        return result_json
    
    def _correct_str_format(self, txt):
        txt = txt.replace("\'", "\"")
        return txt
    
