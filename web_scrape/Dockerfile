FROM python:3.12.8-slim-bullseye

WORKDIR /app

COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

COPY .env /app

# Expose only the single port the app runs on
EXPOSE 8092

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8092"]