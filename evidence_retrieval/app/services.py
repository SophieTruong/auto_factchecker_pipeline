from typing import Optional, List   
from model import Claim, SearchResponse, SingleClaimSearchResult, ClaimSearchResult

from database.queries import (
    search, 
    release_collection, 
    list_collections,
    set_properties
)
from database.db_client import sentence_transformer_ef
from database.collection import get_collection

from translator import translate_claim

from make_request import make_request

from utils import validate_and_fix_date, logger

from datetime import datetime
import dotenv
import os

dotenv.load_dotenv(dotenv.find_dotenv())
WEB_SEARCH_URL = os.getenv("WEB_SEARCH_URL")

# Const names
_COLLECTION_NAME = 'text_embeddings'
_VECTOR_FIELD_NAME = 'embedding'

class SemanticSearchService:
    def __init__(self, distance_threshold: float = 50.00):
        self.distance_threshold = distance_threshold

    async def semantic_search(self, search_input: Claim) -> ClaimSearchResult:        
        # vector db search  
        search_results = self._vector_db_search(search_input)
        
        logger.info(f"DEBUG search_results: {search_results}")
        
        # web search
        web_search_results = await self._web_search(search_input)
        
        logger.info(f"web_search_results: {web_search_results}")
        
        # parse results
        claim_search_result = ClaimSearchResult(
                claim=search_input.claim,
                vector_db_results=search_results[0], # TODO: properly 
                web_search_results=web_search_results
            )
        
        return claim_search_result
    
    async def _web_search(self, search_input: Claim) -> dict:

        web_search_results = await make_request(WEB_SEARCH_URL, search_input.model_dump())
        
        return web_search_results
    
    def _vector_db_search(self, search_input: Claim) -> List[Optional[SingleClaimSearchResult]]:
        translated_claim = translate_claim(search_input.claim)
        
        query_vectors = sentence_transformer_ef.encode_queries([translated_claim])
        
        factcheck_date =  validate_and_fix_date(search_input.timestamp)
        
        logger.info(f"Factcheck date:  {factcheck_date}")
        
        #create collection
        collection = get_collection(_COLLECTION_NAME)
        
        collection.load()
        
        # alter ttl properties of collection level
        set_properties(collection)

        # show collections
        list_collections()

        # search
        search_results = search(collection, _VECTOR_FIELD_NAME, query_vectors, factcheck_date)
        
        logger.info(f"search_results for evidence retrieval module: {search_results}")
       
        # parse results
        parsed_results = []
       
        for i, result in enumerate(search_results):
            
            if len(result) == 0:
                
                parsed_results.append([])
            
            else:
                
                single_claim_search_results = []
                
                for item in result:
                    
                    print(f"DEBUG: item: {item}")
                    
                    # single_claim_search_result = []
                    # SingleClaimSearchResult(
                    #     id=item["id"],
                    #     distance=item["distance"],
                    #     source=item["entity"]["source"],
                    #     timestamp=item["entity"]["timestamp"],
                    #     text=item["entity"]["text"],
                    #     label=item["entity"]["label"],
                    #     url=None
                    #     )
                    
                    # single_claim_search_results.append(single_claim_search_result)
                
                parsed_results.append(single_claim_search_results)
            
            logger.info(f"DEBUG: i = {i}")
            
        release_collection(collection)
       
        return parsed_results
    
