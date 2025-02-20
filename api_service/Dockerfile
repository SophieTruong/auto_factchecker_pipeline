FROM python:3.12-slim-bullseye

# Set working directory in the container
WORKDIR /app

RUN apt-get update && apt-get install -y git

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update --allow-insecure-repositories -y && apt-get install apt-file -y && apt-file update && apt-get install -y python3-dev build-essential

# Install dependencies:
COPY requirements.txt .
RUN pip install -U pip setuptools wheel
RUN pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt
    
# Copy the rest of the application
COPY ./app /app

# Copy env file
COPY .env .

COPY test_script.py .

# Set Python path
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application : CMD ["tail", "-f", "/dev/null"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "debug"]
