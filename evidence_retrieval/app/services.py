from typing import Optional, List   
from model import Claim, SearchResponse, SingleClaimSearchResult, ClaimSearchResult

from pymilvus.model.hybrid import BGEM3EmbeddingFunction

from milvus_hybrid_retrieval import HybridRetriever # hybrid search and returned filtered and ranked results from milvus

from web_search_retrieval import rank_web_search_results

from translator import translate_claim

from make_request import make_request

from utils import validate_and_mk_hybrid_date, get_date_from_hybrid_ts, logger

from datetime import datetime
import dotenv
import os

dotenv.load_dotenv(dotenv.find_dotenv())

MODEL_DIR = os.getenv("MODEL_DIR")

WEB_SEARCH_URL = os.getenv("WEB_SEARCH_URL")

# Const names
_COLLECTION_NAME = 'text_embeddings'
_VECTOR_FIELD_NAME = 'embedding'

class SemanticSearchService:
    def __init__(self):
        pass

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
                vector_db_results=search_results,
                web_search_results=web_search_results
            )
        
        return claim_search_result
    
    async def _web_search(self, search_input: Claim) -> dict:

        web_search_results = await make_request(WEB_SEARCH_URL, search_input.model_dump())
        
        ranked_web_search_results = rank_web_search_results(web_search_results)
        
        return ranked_web_search_results
    
    def _vector_db_search(self, search_input: Claim) -> List[Optional[SingleClaimSearchResult]]:
        
        logger.info(f"Before dense embedding function INIT")
        
        logger.info(f"MODEL_DIR: {MODEL_DIR}")
        
        dense_ef = BGEM3EmbeddingFunction(
            model_name="BAAI/bge-m3",
            device="cpu",
            normalize_embeddings=True,
            cache_dir=MODEL_DIR,
        )
        
        standard_retriever = HybridRetriever(
            uri="http://milvus_standalone:19530",
            collection_name="milvus_hybrid",
            dense_embedding_function=dense_ef,
            # dense_embedding_function=sentence_transformer_ef,
        )
        
        query = search_input.claim
        
        filter = "created_at <= {created_at}"
        
        filter_params = {"created_at": validate_and_mk_hybrid_date(search_input.timestamp)}
    
        results = standard_retriever.search(query, k=10, mode="hybrid", filter=filter, filter_params=filter_params)
                
        logger.info(f"search_results for evidence retrieval module: {results}")
       
        # parse results
        parsed_results = []
       
        for i, result in enumerate(results):
            
            if len(result) == 0:
                
                parsed_results.append([])
            
            else:
                
                # single_claim_search_results = []
                
                # for item in result:
                    
                print(f"DEBUG: result: {result}")
                    
                single_claim_search_result = SingleClaimSearchResult(
                    id=result["id"],
                    score=result["score"],
                    source=result["source"],
                    created_at=get_date_from_hybrid_ts(result["created_at"]), # int to datetime
                    text=result["text"],
                    label=result["label"],
                    url=result["url"]
                    )
                    
                    # single_claim_search_results.append(single_claim_search_result)
                
                parsed_results.append(single_claim_search_result)
            
            logger.info(f"DEBUG: i = {i}")
                   
        return parsed_results
    
