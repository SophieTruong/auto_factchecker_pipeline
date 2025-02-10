import mlflow
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
import os
from datetime import datetime

# MLflow setup
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_NAME = "test_model"

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
print(f"MLflow tracking URI: {MLFLOW_TRACKING_URI}")

def generate_sample_data(n_samples=1000):
    """Generate synthetic data for binary classification"""
    np.random.seed(42)
    
    # Generate random features
    X = np.random.randn(n_samples, 2)
    
    # Generate target: 1 if sum of features > 0, else 0
    y = (X.sum(axis=1) > 0).astype(int)
    
    return X, y

def train_and_log_model():
    """Train a simple model and log it to MLflow"""
    print("Starting training process...")
    
    # Generate data
    X, y = generate_sample_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Start MLflow run
    with mlflow.start_run() as run:
        print(f"MLflow run ID: {run.info.run_id}")
        
        # Train model
        model = LogisticRegression(random_state=42)
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        
        # Log parameters
        mlflow.log_params({
            "model_type": "LogisticRegression",
            "random_state": 42,
            "train_size": len(X_train)
        })
        
        # Log metrics
        mlflow.log_metrics({
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall
        })
        
        # Log model
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name=MODEL_NAME
        )
        
        print(f"Model metrics:")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        
        # Transition to production if metrics are good
        client = mlflow.tracking.MlflowClient()
        latest_version = client.get_latest_versions(MODEL_NAME, stages=["None"])[0]
        
        if accuracy > 0.7:  # Simple threshold for testing
            print(f"Model accuracy {accuracy:.4f} exceeds threshold 0.7, promoting to production")
            client.transition_model_version_stage(
                name=MODEL_NAME,
                version=latest_version.version,
                stage="Production"
            )
        
        print(f"Model training and logging complete")
        return run.info.run_id

def test_model_inference(run_id):
    """Test model inference using MLflow"""
    print("\nTesting model inference...")
    
    # Load model from MLflow
    model_uri = f"runs:/{run_id}/model"
    loaded_model = mlflow.sklearn.load_model(model_uri)
    
    # Generate test data
    X_test, _ = generate_sample_data(n_samples=5)
    
    # Make predictions
    predictions = loaded_model.predict(X_test)
    
    print(f"Test predictions for 5 samples: {predictions}")
    return predictions

if __name__ == "__main__":
    print("Starting MLflow experiment...")
    
    # Create experiment if it doesn't exist
    experiment_name = "test_experiment"
    try:
        mlflow.create_experiment(experiment_name)
    except:
        pass
    
    mlflow.set_experiment(experiment_name)
    
    try:
        # Train and log model
        run_id = train_and_log_model()
        
        # Test inference
        test_model_inference(run_id)
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")