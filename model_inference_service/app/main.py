from typing import List, Tuple

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model import InferenceResult, ModelMetadata
from utils import load_yaml_file, parse_datetime

import mlflow
import asyncio
import dotenv
import os
dotenv.load_dotenv(dotenv.find_dotenv())

# Load model
MODEL_URI = os.getenv("MODEL_URI")
MODEL_METADATA = os.getenv("MODEL_METADATA")    
print(f"MODEL_URI: {MODEL_URI}")
print(f"MODEL_METADATA: {MODEL_METADATA}")

model = mlflow.pyfunc.load_model(MODEL_URI)
model_metadata = load_yaml_file(MODEL_METADATA)

model_metadata = ModelMetadata(
    model_name=model_metadata["name"],
    model_version=str(model_metadata["version"]),
    model_path=model_metadata["source"],
    created_at=parse_datetime(model_metadata["creation_timestamp"])
)

# Setup FastAPI app
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict(request: List[str]) -> dict:
    predictions = await asyncio.to_thread(model.predict, request)
    
    # Convert torch tensor to Python list/dict
    predictions = predictions.cpu().numpy().tolist()
    
    return {
        "model_metadata": model_metadata,
        "inference_results": [InferenceResult(label=p) for p in predictions]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
