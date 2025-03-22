from fastapi import FastAPI, HTTPException, Depends

from pydantic.functional_validators import BeforeValidator

from typing_extensions import Annotated

from dateutil.parser import parse

from datetime import datetime

from database.mongodb import MongoDBManager

from pipeline_metric_service import PipelineMetricService

from model import PipelineMetricsResponse

import motor.motor_asyncio

app = FastAPI()

# Initialize MongoDBManager and load collections
try:
    mongo_manager = MongoDBManager()
    client = mongo_manager.connect_to_db()
    db = client.model_monitoring
    
except Exception as e:
    print(f"Error initializing MongoDBManager: {e}")
    raise

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
# Source: https://github.com/mongodb-developer/mongodb-with-fastapi/blob/master/app.py
PyObjectId = Annotated[str, BeforeValidator(str)]

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get(
    "/pipeline_metrics",
    response_model=PipelineMetricsResponse,
)
async def get_pipeline_metrics(start_date: str, end_date: str, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(MongoDBManager)):
    """
    Get the record for a specific student, looked up by `id`.
    """
    # validate start_date and end_date
    try:
        
        start_date = parse(start_date)
        
        end_date = parse(end_date)
        
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise HTTPException(status_code=400, detail="Invalid date format")
        
        if start_date > end_date:
        
            raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    except ValueError as e:
    
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
        
    # validate start_date and end_date
    pipeline_metric_service = PipelineMetricService(
        db, 
        start_date, 
        end_date
        )
        
    return await pipeline_metric_service.get_metrics()