from services.evidence_retrieval_rpc_client import EvidenceRetrievalRpcClient
from models.semantic_search_input import SemanticSearchInput
from utils.app_logging import logger
from services.publish_monitoring_event import PublishMonitoringEvent

import json
from typing import List, Optional, Dict, Any

class EvidenceRetrievalService:
    """
    Service class to manage the evidence retrieval RPC client with lazy initialization.
    """
    def __init__(self):
        self.rpc_client = EvidenceRetrievalRpcClient()
        self.publish_monitoring_event = PublishMonitoringEvent()
        
    async def ensure_connections(self):
        """Ensure all RabbitMQ connections are established"""
        if not self.rpc_client.is_connected:
            await self.rpc_client.connect()
            
        if not self.publish_monitoring_event.is_connected:
            await self.publish_monitoring_event.connect()
            
    async def close_connections(self):
        """Close all RabbitMQ connections"""
        if hasattr(self, 'rpc_client') and self.rpc_client.is_connected:
            await self.rpc_client.close()
            
        if hasattr(self, 'publish_monitoring_event') and self.publish_monitoring_event.is_connected:
            await self.publish_monitoring_event.close()
    
    async def process_search_request(self, claim: SemanticSearchInput) -> Dict[str, Any]:
        """
        Process a single search request through the RPC client.
        
        Args:
            claim: The semantic search input claim
            
        Returns:
            The decoded search result
        """
        await self.ensure_connections()
        
        try:
            logger.info(f"Sending search request for claim: {claim.claim}")
            
            # Get the raw result as bytes
            result_bytes = await self.rpc_client.get_search_result(claim)
            
            # Decode the bytes to JSON
            result_json = json.loads(result_bytes.decode('utf-8'))
            
            # Produce the metrics logs      
            vector_db_search_scores = [value["score"] for value in result_json['vector_db_results']]
                        
            vector_db_search_scores_min = min(vector_db_search_scores) if vector_db_search_scores else 0
            
            vector_db_search_scores_max = max(vector_db_search_scores) if vector_db_search_scores else 0
            
            vector_db_search_scores_mean = sum(vector_db_search_scores) / (len(vector_db_search_scores) if len(vector_db_search_scores) > 0 else 1)
            
            web_search_cosine_similarity = [value["similarity"] for value in result_json['web_search_results']]
                        
            web_search_cosine_similarity_min = min(web_search_cosine_similarity) if web_search_cosine_similarity else 0
            
            web_search_cosine_similarity_max = max(web_search_cosine_similarity) if web_search_cosine_similarity else 0
            
            web_search_cosine_similarity_mean = sum(web_search_cosine_similarity) / (len(web_search_cosine_similarity) if len(web_search_cosine_similarity) > 0 else 1)
                        
            # Log success to monitoring
            await self.publish_monitoring_event.publish_event(
                event_type="complete",
                module_name="evidence_retrieval",
                event_data={
                    "claim_text": claim.claim,
                    "status": "success",
                    "vector_db_search_scores_min": vector_db_search_scores_min,
                    "vector_db_search_scores_max": vector_db_search_scores_max,
                    "vector_db_search_scores_mean": vector_db_search_scores_mean,
                    "web_search_cosine_similarity_min": web_search_cosine_similarity_min,
                    "web_search_cosine_similarity_max": web_search_cosine_similarity_max,
                    "web_search_cosine_similarity_mean": web_search_cosine_similarity_mean
                }
            )
            
            return result_bytes
            
        except Exception as e:
            logger.error(f"Error processing search request: {e}")
            
            # Log error to monitoring
            await self.publish_monitoring_event.publish_event(
                event_type="error",
                module_name="evidence_retrieval",
                event_data={
                    "claim_text": claim.claim,
                    "status": "error",
                    "error": str(e)
                }
            )
            
            raise 