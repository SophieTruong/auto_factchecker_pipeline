from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ModelMetrics(BaseModel):
    """Metrics for a single model"""
    start_date: datetime
    end_date: datetime
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    f1_micro: float
    f1_macro: float
    f1_weighted: float
    sample_count: int

class EvidenceRetrievalMetrics(BaseModel):
    """Metrics for evidence retrieval model"""
    start_date: datetime
    end_date: datetime
    query_count: int
    freq_empty_milvus_hybrid_search: float
    freq_empty_web_search: float
    frq_close_match_websearch: float
    frq_close_match_milvus_hybrid_search: float
    n_exact_match_websearch: int
    milvus_hybrid_search_score_max: float
    web_search_score_max: float
    example_claim_no_evidence_milvus_hybrid_search: Optional[Dict[str, Any]]
    example_claim_no_evidence_web_search: Optional[Dict[str, Any]]
    example_claim_high_match_websearch: Optional[Dict[str, Any]]
    example_claim_high_match_milvus_hybrid_search: Optional[Dict[str, Any]]
    
class PipelineMetricsResponse(BaseModel):
    """Response model for pipeline metrics endpoint"""
    claim_detection_metrics: Optional[ModelMetrics] = None
    evidence_retrieval_metrics: Optional[EvidenceRetrievalMetrics] = None
