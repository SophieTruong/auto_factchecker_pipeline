from typing import Dict, List
from uuid import UUID
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy.orm import Session
from database.queries import get_last_log, write_metric
from make_request import make_request
from metric_calculator import calculate_metrics

from model import InputData, ClaimModelMetric
    
class ClaimModelMonitoringService:
    """
    The service class to get the claim detectionmodel monitoring data from the main API and save it to the SQLite database
    """
    def __init__(self, db: Session, url: str, start_date: datetime | None = None, end_date: datetime | None = None):
        self.db = db
        self.url = url
        self.start_date = start_date
        self.end_date = end_date

    async def get_metrics(self) -> List[ClaimModelMetric]:
        """
        Get metrics from the main API and save them to the SQLite database
        """        
        # Call get log to calculate start and end date
        self._get_start_and_end_date()

        print(f"self.start_date: {self.start_date}, self.end_date: {self.end_date}")
        # Make an API request to the main API to get the model monitoring data using start and end date
        responses = await self._get_model_monitoring_data(self.url)
        
        parsed_responses = [InputData(**response) for response in responses]
        
        # Calculate metrics with respects to models_id
        grouped_data_by_model = self._group_data_by_model(parsed_responses)
        
        metrics_by_model = self._calculate_metrics(grouped_data_by_model)
        
        # Save metrics to SQLite database
        self._save_metrics(metrics_by_model)
        
        return metrics_by_model
    
    def write_to_model_training_orchestrator(self, metrics: List[ClaimModelMetric]) -> bool:
        """
        Write metrics to the model training orchestrator
        """
        pass
    
    def _get_start_and_end_date(self):
        """
        The helper function determine the start and end date in the case either of them is not provided
        """
        # Get end date
        current_date = datetime.now()
        
        # Get last log date (with error handling)
        try:
            last_log = get_last_log(self.db)
            last_log_date = last_log.end_date if last_log else None
            print(f"Last log date: {last_log_date}")
        except Exception as e:
            print(f"Error getting last log: {e}")
            last_log_date = None
        
        # Set default window
        default_window = timedelta(days=30)
        
        # Handle different date scenarios
        if not self.end_date:
            self.end_date = current_date
            
        if not self.start_date:
            if last_log_date and last_log_date < current_date:
                self.start_date = last_log_date
            else:
                self.start_date = self.end_date - default_window
        
    async def _get_model_monitoring_data(self, url: str)-> List[dict]:
        start_date = self.start_date.strftime("%Y-%m-%d")
        end_date = self.end_date.strftime("%Y-%m-%d")
        responses = await make_request(url, start_date, end_date)
        return responses

    def _group_data_by_model(self, responses: List[InputData])-> Dict[str, Dict[str, List[bool]]]:
        """
        Group predictions and annotations by model_id.
        
        Returns:
            Dict[str, Dict[str, List[bool]]]: Dictionary with model_ids as keys and 
                predictions/annotations as nested dictionary
        """
        grouped_data = defaultdict(lambda: {"annotations": [], "predictions": []})
        
        for response in responses:
            model_id = response.model_id
            grouped_data[model_id]["annotations"].append(response.annotation_label)
            grouped_data[model_id]["predictions"].append(response.inference_label)
        
        return grouped_data
    
    # Update your existing code
    def _calculate_metrics(self, grouped_data_by_model: Dict[str, Dict[str, List[bool]]])-> List[ClaimModelMetric]:
        """Process responses and calculate metrics by model"""        
        # Calculate metrics for each model
        model_metrics = []
        for model_id, data in grouped_data_by_model.items():
            metrics = calculate_metrics(data["predictions"], data["annotations"])
            model_metrics.append(ClaimModelMetric(
                start_date=self.start_date,
                end_date=self.end_date, 
                model_id=model_id,
                metrics=metrics
            ))
        return model_metrics

    def _save_metrics(self, metrics: List[ClaimModelMetric]) -> bool:
        """
        Save metrics to SQLite database
        """
        try:
            for metric in metrics:
                db_metric = metric.model_dump()
                for key, value in db_metric["metrics"].items():
                    db_metric[key] = value
                db_metric.pop("metrics")
                write_metric(self.db, db_metric)
            return True
        except Exception as e:
            print(f"Error saving metrics: {e}")
            return False
