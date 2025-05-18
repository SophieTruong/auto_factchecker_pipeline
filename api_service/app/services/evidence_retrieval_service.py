from typing import Dict, Any

from services.evidence_retrieval_rpc_client import EvidenceRetrievalRpcClient
from models.semantic_search_input import SemanticSearchInput
from utils.app_logging import logger

class EvidenceRetrievalService:
    """
    Service class to manage the evidence retrieval RPC client with lazy initialization.
    """
    def __init__(self):
        self.rpc_client = EvidenceRetrievalRpcClient()
            
    async def process_search_request(self, claim: SemanticSearchInput) -> Dict[str, Any]:
        """
        Process a single search request through the RPC client.
        
        Args:
            claim: The semantic search input claim
            
        Returns:
            The decoded search result
        """        
        try:
            logger.info(f"Sending search request for claim: {claim.claim}")
            
            # Get the raw result as bytes
            result_bytes = await self.rpc_client.get_search_result(claim)
            
            return result_bytes
        
        except Exception as e:
            
            logger.error(f"Error processing search request: {e}")
            
            raise 
