import json
from typing import Dict, Any, Optional
from datetime import datetime

from database.mongodb import MongoDBManager

class MonitoringService:
    """
    Service class to process monitoring messages before inserting into the database.
    Handles validation, transformation, and database operations for monitoring events.
    """
    
    @staticmethod
    def parse_message_body(message_body: str) -> Optional[Dict[str, Any]]:
        """
        Process a raw message from RabbitMQ, validate it, and return the parsed data.
        
        Args:
            message_body: Raw message body from RabbitMQ
            
        Returns:
            Parsed message as a dictionary or None if invalid
        """
        try:
            # Convert bytes to string if needed, with proper encoding
            if isinstance(message_body, bytes):
                message_str = message_body.decode('utf-8')
            else:
                message_str = message_body
            
            # Debug the raw message
            print(f"Raw message before parsing: {message_str}")
            
            # Parse the message with proper encoding
            parsed_message = json.loads(message_str)
            
            # Debug the parsed message
            print(f"Parsed message: {parsed_message}")
            
            return parsed_message
        except json.JSONDecodeError as e:
            print(f"Error parsing message: {e}")
            print(f"Invalid message body: {message_body}")
            return None
        except UnicodeDecodeError as e:
            print(f"Unicode decoding error: {e}")
            # Try with a different encoding as fallback
            try:
                if isinstance(message_body, bytes):
                    message_str = message_body.decode('iso-8859-15')  # Try Nordic/Baltic encoding
                    parsed_message = json.loads(message_str)
                    return parsed_message
            except Exception as inner_e:
                print(f"Failed alternate encoding attempt: {inner_e}")
            return None
        except Exception as e:
            print(f"Unexpected error processing message: {e}")
            return None
    
    @staticmethod
    def validate_message(message: Dict[str, Any]) -> bool:
        """
        Validate that the message has the required fields.
        
        Args:
            message: The parsed message dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["event_type", "module_name"]
        
        # Check for required fields
        for field in required_fields:
            if field not in message:
                print(f"Message missing required field: {field}")
                return False
                
        return True
    
    @staticmethod
    async def handle_evidence_retrieval_metrics(db_manager:MongoDBManager, metrics: Dict[str, Any]) -> bool:
        """
        Process and store evidence retrieval metrics.
        
        Args:
            metrics: Evidence retrieval metrics data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add timestamp if not present
            if "timestamp" not in metrics:
                metrics["timestamp"] = datetime.now().isoformat()
            
            
            # Log the metrics for debugging
            print(f"Processing evidence retrieval metrics: {metrics}")
            
            # Additional validation specific to evidence retrieval
            required_fields = ["event_type", "module_name"]
            for field in required_fields:
                if field not in metrics:
                    print(f"Evidence metrics missing required field: {field}")
                    return False
            
            # Store in database
            await db_manager.insert_evidence_metrics(metrics)
            print(f"Successfully stored evidence retrieval metrics in database")
            return True
        except Exception as e:
            print(f"Error handling evidence metrics: {e}")
            return False
    
    @staticmethod
    async def handle_claim_annotation_metrics(db_manager: MongoDBManager, metrics: Dict[str, Any]) -> bool:
        """
        Process and store claim annotation metrics.
        
        Args:
            metrics: Claim annotation metrics data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add timestamp if not present
            if "timestamp" not in metrics:
                metrics["timestamp"] = datetime.now().isoformat()
            
            # Log the metrics for debugging
            print(f"Processing claim annotation metrics: {metrics}")
            
            # Additional validation specific to claim annotations
            data = metrics["data"]
            if "claim_ids" not in data or not data["claim_ids"]:
                print("Claim metrics missing claim_ids field")
                return False
                
            if "claim_annotations" not in data or not data["claim_annotations"]:
                print("Claim metrics missing claim_annotations field")
                return False
                
            if "claim_model_inferences" not in data or not data["claim_model_inferences"]:
                print("Claim metrics missing claim_model_inferences field")
                return False
                
            # Check that arrays have the same length
            if len(data["claim_ids"]) != len(data["claim_annotations"]) or \
               len(data["claim_ids"]) != len(data["claim_model_inferences"]):
                print("Claim metrics arrays have different lengths")
                return False
            
            # The database function handles the transformation to individual records
            await db_manager.insert_claim_metrics({**data, "timestamp": metrics["timestamp"]})
            print(f"Successfully stored claim annotation metrics in database")
            return True
        except Exception as e:
            print(f"Error handling claim metrics: {e}")
            return False 