# Claim Model Monitor Service: it should only query claims with inference and annotation and returns result json
from typing import List, Optional
from sqlalchemy.orm import Session

from models.claim_model_monitoring import ClaimModelMonitoring
from database.crud import get_claims_with_inference_and_annotation

from utils.validator import validate_date_range
from utils.app_logging import logger

class ClaimModelMonitoringService:
    def __init__(self, db: Session):
        self.db = db

    def parse_results(self, results) -> List[dict]:
        return [result._asdict() for result in results]

    def get_claims_with_inference_and_annotation(self, start_date: str, end_date: str) -> Optional[List[ClaimModelMonitoring]]:
        """ Get claims with inference and annotation by date range """
        try:
            with self.db.begin():
                start_date, end_date = validate_date_range(start_date, end_date)
                results = get_claims_with_inference_and_annotation(self.db, start_date, end_date)
                parsed_results = self.parse_results(results)
                parsed_results = [ClaimModelMonitoring(
                    claim_id=result['claim_id'],
                    claim_text=result['claim_text'],
                    model_id=result['model_id'],
                    annotation_label=result['annotation_label'],
                    inference_label=result['inference_label'],
                ) for result in parsed_results]
                return parsed_results
        except Exception as e:
            logger.error(f"Error getting claims with inference and annotation: {e}")
            return None