FROM python:3.12.8-slim-bullseye as build

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12.8-slim-bullseye

WORKDIR /app

# Copy virtual environment from build stage
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy database code
COPY ./app/main.py \
    ./app/model.py \
    ./app/metric_calculator.py \
    ./app/pipeline_metric_service.py \
    /app/

COPY ./app/database /app/database

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set Python path
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 8096

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8096"]