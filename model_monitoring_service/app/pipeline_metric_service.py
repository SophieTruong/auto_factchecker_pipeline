from datetime import datetime
import pandas as pd

import motor.motor_asyncio

from metric_calculator import calculate_metrics
from model import ModelMetrics, EvidenceRetrievalMetrics, PipelineMetricsResponse

# Set display options
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.max_rows', None)     # Show all rows
pd.set_option('display.width', None)        # Width of the display in characters
pd.set_option('display.max_colwidth', None) # Full width of each column

class PipelineMetricService:
    def __init__(
        self, 
        db: motor.motor_asyncio.AsyncIOMotorDatabase, 
        start_date: datetime, 
        end_date: datetime
        ):
        self.db = db
        self.start_date= start_date
        self.end_date = end_date
    
    async def get_claim_metrics(self) -> ModelMetrics:
        claim_metrics = await self.db.get_claim_metrics(self.start_date, self.end_date)
        
        print(f"*** MYDEBUG claim_metrics: {claim_metrics}")
        
        if claim_metrics and isinstance(claim_metrics, list) and len(claim_metrics) > 0:
            claim_metrics_df = pd.DataFrame(claim_metrics)
            
            # For annotations: use majority voting: e.g. if 2 out of 3 annotations for same claim_model_id and claim_id are positive, then the annotation is positive
            claim_mv_annotation_prediction_df = claim_metrics_df.groupby(['claim_model_id', 'claim_id']).agg({
                    'annotation': lambda x: x.mode()[0], # Majority voting
                    'prediction': lambda x: x.mode()[0] # Majority voting
                }).reset_index()
            
            print(f"*** MYDEBUG claim_mv_annotation_prediction_df: {claim_mv_annotation_prediction_df}")
            
            # Number of claims
            sample_count = claim_mv_annotation_prediction_df.shape[0]
            
            # Calculate metrics
            prediction_list = claim_mv_annotation_prediction_df["prediction"].tolist()
            annotation_list = claim_mv_annotation_prediction_df["annotation"].tolist()
            
            metrics = calculate_metrics(prediction_list, annotation_list)
            
            model_metrics = ModelMetrics(
                start_date=self.start_date,
                end_date=self.end_date,
                sample_count=sample_count,
                **metrics
            )
            
            print(f"Parsed claim metrics: {model_metrics}")
        else:
            print(f"No claim metrics found")
            model_metrics = ModelMetrics(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
        return model_metrics
    
    async def get_evidence_metrics(self) -> EvidenceRetrievalMetrics:
        evidence_metrics = await self.db.get_evidence_metrics(self.start_date, self.end_date)
        
        metrics_data = [evidence_metric["data"] for evidence_metric in evidence_metrics]
        
        query_count = len(metrics_data)
        
        sample_metrics = {}
        
        # Are we more likely to find empty search results from milvus_hybrid_search? vector_db_search_size = web_search_size = 0
        sample_metrics["freq_empty_milvus_hybrid_search"] = sum(1 if metric["vector_db_search_size"] == 0 else 0 for metric in metrics_data) / len(metrics_data) if len(metrics_data) > 0 else 0
        
        # Are we more likely to find empty search results from web_search? vector_db_search_size = web_search_size = 0
        sample_metrics["freq_empty_web_search"] = sum(1 if metric["web_search_size"] == 0 else 0 for metric in metrics_data) / len(metrics_data) if len(metrics_data) > 0 else 0
        
        # Are we more likely to find close match in websearch? Frequency of cosine similarity > 0.6 <= TODO: Justify this magic number
        sample_metrics["frq_close_match_websearch"] = sum(1 if metric["web_search_cosine_similarity_max"] > 0.6 else 0 for metric in metrics_data) / len(metrics_data) if len(metrics_data) > 0 else 0
        
        # Are we more likely to find close match in websearch? Frequency of reranker score > 0.03 <= TODO: Justify this magic number
        sample_metrics["frq_close_match_milvus_hybrid_search"] = sum(1 if metric["vector_db_search_scores_max"] > 0.03 else 0 for metric in metrics_data) / len(metrics_data) if len(metrics_data) > 0 else 0

        # How many exact match we found from websearch? 
        sample_metrics["n_exact_match_websearch"] = sum(1 if metric["web_search_cosine_similarity_max"] == 1 else 0 for metric in metrics_data)
        
        # What is the max score of the milvus_hybrid_search? >> Do we have high match in the search at all
        sample_metrics["milvus_hybrid_search_score_max"] = max(metric["vector_db_search_scores_max"] for metric in metrics_data) if len(metrics_data) > 0 else 0
        
        # What is the max score of the web_search? >> Do we have high match in the search at all
        sample_metrics["web_search_score_max"] = max(metric["web_search_cosine_similarity_max"] for metric in metrics_data) if len(metrics_data) > 0 else 0
        
        # Give an example of query claim with no evidence found from milvus_hybrid_search
        sample_metrics["example_claim_no_evidence_milvus_hybrid_search"] = next((metric for metric in metrics_data if metric["vector_db_search_size"] == 0), None)
        
        # Give an example of query claim with no evidence found from web_search
        sample_metrics["example_claim_no_evidence_web_search"] = next((metric for metric in metrics_data if metric["web_search_size"] == 0), None)
        
        # Give an example of query claim with high match in websearch
        sample_metrics["example_claim_high_match_websearch"] = next((metric for metric in metrics_data if metric["web_search_cosine_similarity_max"] > 0.6), None)
        
        # Give an example of query claim with high match in milvus_hybrid_search
        sample_metrics["example_claim_high_match_milvus_hybrid_search"] = next((metric for metric in metrics_data if metric["vector_db_search_scores_max"] > 0.03), None)
        
        evidence_retrieval_metrics = EvidenceRetrievalMetrics(
            start_date=self.start_date,
            end_date=self.end_date,
            query_count=query_count,
            **sample_metrics
        )
            
        return evidence_retrieval_metrics
    
    async def get_metrics(self) -> PipelineMetricsResponse:
        claim_metrics = await self.get_claim_metrics()
        evidence_metrics = await self.get_evidence_metrics()
        return PipelineMetricsResponse(
            claim_detection_metrics=claim_metrics,
            evidence_retrieval_metrics=evidence_metrics
        )
    