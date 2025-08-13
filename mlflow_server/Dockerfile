FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt


# Copy training script
COPY test_train.py .

# Set environment variables
ENV MLFLOW_TRACKING_URI=http://mlflow_server:5000

# Run training script
CMD ["python", "test_train.py"]