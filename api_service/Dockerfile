# Stage 1: Build
FROM python:3.12-slim-bullseye AS build

# Set working directory in the container
WORKDIR /app

# Install build dependencies in a single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt
    
# Stage 2: Runtime
FROM python:3.12-slim-bullseye

WORKDIR /app

# Copy virtual environment from build stage
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app

# Copy only necessary files
COPY ./app /app
COPY .env .
COPY test_script.py .

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application : CMD ["tail", "-f", "/dev/null"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "debug"]
