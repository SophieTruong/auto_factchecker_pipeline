FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

COPY .env .

VOLUME ["/app/model_training_service"]

CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"] 