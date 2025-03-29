import motor.motor_asyncio

from datetime import datetime
import time
from typing import List, Dict, Any

import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

MONGO_URI = os.getenv("MONGO_URI")

class MongoDBManager:
    def __init__(self, max_retries: int = 5, retry_delay: int = 3):
        self.client: motor.motor_asyncio.AsyncIOMotorClient | None = None 
        self.db: motor.motor_asyncio.AsyncIOMotorDatabase | None = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.is_connected = False
        
    def connect_to_db(self) -> motor.motor_asyncio.AsyncIOMotorClient:
        for attempt in range(self.max_retries):
            try:
                # Use motor's async client instead of PyMongo
                # Make sure authSource is specified properly
                connection_uri = MONGO_URI
                
                if "authSource" not in connection_uri and "?" not in connection_uri:
                    connection_uri += "?authSource=admin"
                elif "authSource" not in connection_uri and "?" in connection_uri:
                    connection_uri += "&authSource=admin"
                
                print(f"Connecting to MongoDB with URI: {connection_uri.replace(connection_uri.split('@')[0], '***:***@')}")
                
                # Create async MongoDB client
                self.client = motor.motor_asyncio.AsyncIOMotorClient(
                    connection_uri,
                    serverSelectionTimeoutMS=5000  # 5 second timeout
                )
                
                # Test the connection using async operation
                self.client.admin.command('ping')
                print("Successfully connected to MongoDB")
                self.is_connected = True
                return self.client
            
            except Exception as e:
                print(f"Connection attempt {attempt+1}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print("Failed to connect to MongoDB after maximum retries")
                    raise

    def get_db(self) -> motor.motor_asyncio.AsyncIOMotorDatabase:
        if not self.is_connected:
            self.connect_to_db()
        self.db = self.client["model_monitoring"]
        return self.db

    def get_collection(self, collection_name) -> motor.motor_asyncio.AsyncIOMotorCollection:
        """
        Get a MongoDB collection by name
        """
        db = self.get_db()
        return db[collection_name]

    def get_evidence_collection(self) -> motor.motor_asyncio.AsyncIOMotorCollection:
        """
        Get the evidence retrieval metrics collection
        """
        return self.get_collection("evidence_retrieval_metrics") # not a coroutine

    def get_claim_collection(self) -> motor.motor_asyncio.AsyncIOMotorCollection:
        """
        Get the claim detection metrics collection
        """
        return self.get_collection("claim_detection_metrics") # not a coroutine

    async def insert_evidence_metrics(self, metrics: dict) -> str:
        """
        Insert evidence retrieval metrics into MongoDB
        """
        try:
            # Add timestamp standardization
            if "created_at" not in metrics and "timestamp" in metrics:
                metrics["created_at"] = metrics["timestamp"]
                
            collection = self.get_evidence_collection()
            result = await collection.insert_one(metrics)  # coroutine -> await
            print(f"Inserted evidence metrics with ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            print(f"Error inserting evidence metrics: {e}")
            raise
    
    async def insert_claim_metrics(self, metrics: dict) -> List[str]:
        """
        Insert claim detection metrics into MongoDB
        Each claim is inserted as a separate document
        """
        try:
            processed_metrics = [
                {
                    "created_at": metrics["timestamp"],
                    "claim_model_id": metrics["claim_model_ids"][i],
                    "claim_id": metrics["claim_ids"][i],
                    "annotation": metrics["claim_annotations"][i],
                    "prediction": metrics["claim_model_inferences"][i]
                }
                for i in range(len(metrics["claim_ids"]))
            ]
            
            collection = self.get_claim_collection()
            results = await collection.insert_many(processed_metrics)  # coroutine -> await
            
            print(f"**MYDEBUG_Inserted claim metrics: {results}")
            
            return results.inserted_ids
        except Exception as e:
            print(f"Error inserting claim metrics: {e}")
            raise

    async def get_claim_metrics(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get claim detection metrics for a date range
        """
        try:
            collection = self.get_claim_collection()
            
            # Use AsyncIOMotorCursor correctly
            cursor = collection.find({
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }) # -> return a MotorCursor 
            
            # Collect all documents into a list
            metrics = await cursor.to_list(length=None)
            return metrics
        except Exception as e:
            print(f"Error retrieving claim metrics: {e}")
            raise

    async def get_evidence_metrics(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get evidence retrieval metrics for a date range
        """
        try:
            collection = self.get_evidence_collection()
                        
            # Use AsyncIOMotorCursor correctly
            cursor = collection.find({
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }) # -> return a MotorCursor 
            
            # Collect all documents into a list
            metrics = await cursor.to_list(length=None)
            return metrics
        except Exception as e:
            print(f"Error retrieving evidence metrics: {e}")
            raise
            
    def close(self) -> None:
        """
        Close the MongoDB connection
        """
        if self.client and self.is_connected:
            self.client.close()
            self.is_connected = False
            print("MongoDB connection closed")