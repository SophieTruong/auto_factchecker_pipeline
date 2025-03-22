FROM python:3.12.8-slim-bullseye

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
COPY ./app/rabbitmq_consumer/requirements.txt .

RUN echo "requirements.txt: $(cat requirements.txt)"

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy database code
COPY ./app/rabbitmq_consumer /app/

COPY ./app/database /app/database

COPY .env /app/.env

# Set python path
ENV PYTHONPATH=/app

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the consumer
CMD ["python", "consumer.py"]