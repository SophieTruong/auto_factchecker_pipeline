from utils.base_rcp_client import BaseRpcClient

class ClaimDetectionRCPClient(BaseRpcClient):
    
    async def publish_message(self, data: dict, request_type: str):
        
        message_data = {
            "data": data,
            "request_type": request_type
        }
        
        return await self._rcp_call(
            message_data, 
            "rpc_claim_db_queue"
        )
