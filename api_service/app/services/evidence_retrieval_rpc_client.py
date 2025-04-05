from utils.base_rcp_client import BaseRpcClient

from models.semantic_search_input import SemanticSearchInput

class EvidenceRetrievalRpcClient(BaseRpcClient):
        
    async def get_search_result(self, claim: SemanticSearchInput):
        
        message_data = {
            "claim": claim.model_dump(),
        }
        
        return await self._rcp_call(
            message_data, 
            "rpc_evidence_retrieval_queue"
        )
        