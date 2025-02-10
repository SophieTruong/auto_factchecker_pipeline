FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy training script
COPY app/train.py .

# Set environment variables
ENV MLFLOW_TRACKING_URI=http://mlflow:8080

# Run training script
CMD ["python", "train.py"]