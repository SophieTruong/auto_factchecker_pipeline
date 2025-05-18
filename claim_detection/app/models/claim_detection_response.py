from typing import List, Optional
from pydantic import BaseModel

from .claim import Claim
from .claim_model_inference import ClaimModelInference

class ClaimResponse(BaseModel):
    claim: Claim
    inference: ClaimModelInference
    
class BatchClaimResponse(BaseModel):
    claims: List[Optional[ClaimResponse]]

