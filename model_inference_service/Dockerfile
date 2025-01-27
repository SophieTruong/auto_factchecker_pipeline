FROM python:3.12.8-slim-bullseye

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y git

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

COPY .env /app

# Expose the port the app runs on
EXPOSE 8090

# Command to run the application
VOLUME ["/app/mlruns"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]