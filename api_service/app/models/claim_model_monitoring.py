from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class ClaimModelMonitoring(BaseModel):
    claim_id: UUID
    claim_text: str
    model_id: UUID
    annotation_label: Optional[bool] = None
    inference_label: Optional[bool] = None