from celery import Task
from celery_app import celery_app
import aiohttp
import asyncio
import requests

import time
import dotenv
import os
dotenv.load_dotenv(dotenv.find_dotenv())

MODEL_DIR = os.getenv("MODEL_DIR")
HF_HOME = os.getenv("HF_HOME")
CONDA_ENVS = os.getenv("CONDA_ENVS")
CONDA_PKGS = os.getenv("CONDA_PKGS")

print(f"MODEL_DIR: {MODEL_DIR}")
print(f"HF_HOME: {HF_HOME}")
print(f"CONDA_ENVS: {CONDA_ENVS}")
print(f"CONDA_PKGS: {CONDA_PKGS}")

class ModelMonitorTask(Task):
    def __init__(self):
        pass
    
    def check_model_health(self):
        print("Checking model health")
        try:
            response = requests.get("http://model_monitoring_service:8096/metrics").json()
            print(f"Response: {response}")
            return response["status"] == "healthy"
        except Exception as e:
            print(f"Error checking model health: {e}")
            return False
    
    def run(self):
        print("Monitoring and retraining")
        time.sleep(20)
        return {"status": "success"}

@celery_app.task(base=ModelMonitorTask)
def monitor_claim_model():
    task = ModelMonitorTask()
    if task.check_model_health():
        print("Retraining model")
        task.run()
    print("Monitoring and retraining")
    return {"status": "success"}    