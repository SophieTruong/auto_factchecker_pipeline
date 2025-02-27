from typing import Optional, List   
from model import SearchInput, SearchResponse, SingleClaimSearchResult, ClaimSearchResult

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

from utils import process_factcheck_dates

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

    async def semantic_search(self, search_input: SearchInput) -> SearchResponse:
        factcheck_dates =  process_factcheck_dates([input.timestamp for input in search_input.claims])
        
        # vector db search  
        search_results = self._vector_db_search(search_input)
        
        # web search
        web_search_results = await self._web_search(search_input)
        
        # parse results
        parsed_results = []
        for i, result in enumerate(search_results):
            parsed_results.append(
                ClaimSearchResult(
                    claim=search_input.claims[i].claim,
                    vector_db_results=result,
                    web_search_results=web_search_results["results"][i]
                )
            )
        return SearchResponse(claims=parsed_results)
    
    async def _web_search(self, search_input: SearchInput) -> dict:
        

        web_search_results = await make_request(WEB_SEARCH_URL, search_input.model_dump())
        
        return web_search_results
    
    def _vector_db_search(self, search_input: SearchInput) -> List[Optional[SingleClaimSearchResult]]:
        translated_claims = [translate_claim(c.claim) for c in search_input.claims]
        
        query_vectors = sentence_transformer_ef.encode_queries(translated_claims)

        factcheck_dates =  process_factcheck_dates([input.timestamp for input in search_input.claims])
        
        print(f"Factcheck dates: {factcheck_dates}")
        
        #create collection
        collection = get_collection(_COLLECTION_NAME)
        collection.load()
        
        # alter ttl properties of collection level
        set_properties(collection)

        # show collections
        list_collections()

        # search
        search_results = search(collection, _VECTOR_FIELD_NAME, query_vectors, factcheck_dates)
        
        # parse results
        parsed_results = []
        for i, result in enumerate(search_results):
            if len(result) == 0:
                parsed_results.append([])
            else:
                single_claim_search_results = []
                for item in result:
                    single_claim_search_result = SingleClaimSearchResult(
                        id=item["id"],
                        distance=item["distance"],
                        source=item["entity"]["source"],
                        timestamp=item["entity"]["timestamp"],
                        text=item["entity"]["text"],
                        label=item["entity"]["label"],
                        url=None
                        )
                    single_claim_search_results.append(single_claim_search_result)
                parsed_results.append(single_claim_search_results)
            
        release_collection(collection)
        return parsed_results
    
