# temp stage
FROM python:3.12.2-slim AS builder

WORKDIR /app

# Python will no longer write .pyc files to disk, and keep the development environment nice and clean
ENV PYTHONDONTWRITEBYTECODE 1

# python output i.e. the stdout and stderr streams are sent straight to terminal
ENV PYTHONUNBUFFERED 1

COPY /api \
database/.env database/models.py database/postgres.py database/utils.py \
claim_detection/predict.py \
semantic_search/pgvector_search.py \
/app/

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# final stage
FROM python:3.12.2-slim

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache --no-cache-dir /wheels/* \
&& python -m spacy download fi_core_news_sm

COPY --from=builder \
/app/.env /app/main.py /app/schemas.py /app/crud.py \
/app/models.py /app/postgres.py /app/utils.py \
/app/predict.py /app/pgvector_search.py \
/app/

ENV HF_HOME=xml-roberta-model SENTENCE_TRANSFORMERS_HOME=sentence-transformer-model

EXPOSE 8080
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]
