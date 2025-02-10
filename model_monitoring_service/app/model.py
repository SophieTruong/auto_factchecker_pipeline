from pydantic import BaseModel
from uuid import UUID
from typing import Dict
from datetime import datetime

class InputData(BaseModel):
    claim_id: UUID
    claim_text: str
    model_id: UUID
    annotation_label: int
    inference_label: int

class ClaimModelMetric(BaseModel):
    start_date: datetime
    end_date: datetime
    model_id: UUID
    metrics: Dict[str, float]   

