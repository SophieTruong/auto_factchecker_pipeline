from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends,  HTTPException, status
from sqlalchemy.orm import Session
from services import ClaimModelMonitoringService
from model import ClaimModelMetric
from database.sqlite import get_db, engine, Base, SessionLocal

import os
import dotenv
dotenv.load_dotenv(dotenv.find_dotenv() )

CLAIM_MODEL_MONITORING_SERVICE_URI = os.getenv("CLAIM_MODEL_MONITORING_SERVICE_URI")

# Set up FastAPI
app = FastAPI()

# Set up db dependancies
Base.metadata.create_all(bind=engine)

@app.get("/metrics", response_model=List[ClaimModelMetric])
async def metrics(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: Session = Depends(get_db)
) -> List[ClaimModelMetric]:
    try:
        model_monitoring_service = ClaimModelMonitoringService(db, CLAIM_MODEL_MONITORING_SERVICE_URI, start_date, end_date)
        metrics = await model_monitoring_service.get_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )
    