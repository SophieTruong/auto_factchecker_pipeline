from typing import Optional, List   
from model import SearchResponse, SingleClaimSearchResult, ClaimSearchResult

from database.queries import (
    search, 
    release_collection, 
    list_collections,
    set_properties
)
from database.db_client import model
from database.collection import get_collection, Collection

# Const names
_COLLECTION_NAME = 'text_embeddings'
_VECTOR_FIELD_NAME = 'embedding'

class SemanticSearchService:
    def __init__(self, distance_threshold: float = 50.00):
        self.distance_threshold = distance_threshold

    def semantic_search(self, search_input: dict) -> SearchResponse:
        query_vectors = model.encode(search_input["translated_claims"])
    
        #create collection
        collection = get_collection(_COLLECTION_NAME)
        collection.load()
        
        # alter ttl properties of collection level
        set_properties(collection)

        # show collections
        list_collections()

        # search
        search_results = search(collection, _VECTOR_FIELD_NAME, query_vectors)
        
        # parse results
        parsed_results = []
        for i, result in enumerate(search_results):
            if len(result) == 0:
                parsed_results.append(ClaimSearchResult(
                    claim=search_input["claims"][i],
                    results=[]
                ))
            else:
                single_claim_search_results = []
                for item in result:
                    print(item)
                    if item["distance"] <= self.distance_threshold:
                        single_claim_search_result = SingleClaimSearchResult(
                            id=item["id"],
                            distance=item["distance"],
                            source=item["entity"]["source"],
                            timestamp=item["entity"]["timestamp"],
                            text=item["entity"]["text"],
                                label=item["entity"]["label"]
                            )
                        single_claim_search_results.append(single_claim_search_result)
                claim_search_result = ClaimSearchResult(
                    claim=search_input["claims"][i],
                    results=single_claim_search_results
                )
                parsed_results.append(claim_search_result)
            
        release_collection(collection)
        return SearchResponse(claims=parsed_results)