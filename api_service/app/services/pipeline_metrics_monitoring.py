# Claim Model Monitor Service: it should only query claims with inference and annotation and returns result json
from typing import List, Optional

from models.pipeline_metrics_response import PipelineMetricsResponse

from utils.validator import validate_date_range
from utils.app_logging import logger
from utils.make_request import make_request

import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

MODEL_MONITORING_URI = os.getenv("MODEL_MONITORING_URI")

class PipelineMetricsMonitoringService:
    def __init__(self, start_date: str, end_date: str):
        self.start_date = start_date
        self.end_date = end_date

    async def get_pipeline_metrics(self) -> Optional[PipelineMetricsResponse]:
        try:
            validate_date_range(self.start_date, self.end_date)
            response = await make_request(
                MODEL_MONITORING_URI,
                data={
                    "start_date": self.start_date,
                    "end_date": self.end_date
                },
                method="GET"
            )
            return PipelineMetricsResponse(**response)
        except Exception as e:
            logger.error(f"Error getting pipeline metrics: {e}")
            return None