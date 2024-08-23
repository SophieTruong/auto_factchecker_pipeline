FROM python:3.12.2-slim AS builder

WORKDIR /db

# Python will no longer write .pyc files to disk, and keep the development environment nice and clean
ENV PYTHONDONTWRITEBYTECODE 1

# python output i.e. the stdout and stderr streams are sent straight to terminal
ENV PYTHONUNBUFFERED 1

COPY database/pgvector/db_seed.py \
database/pgvector/postgres.py database/pgvector/models.py database/pgvector/crud.py \
database/pgvector/utils.py database/pgvector/.env \
database/requirements.txt \
./
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /db/wheels -r requirements.txt

FROM python:3.12.2-slim

WORKDIR /db

COPY --from=builder /db/wheels /wheels
COPY --from=builder /db/requirements.txt .
RUN pip install --no-cache --no-cache-dir /wheels/*

COPY --from=builder /db/db_seed.py /db/.env \
/db/postgres.py /db/models.py /db/crud.py /db/utils.py \
./

ENV SENTENCE_TRANSFORMERS_HOME=sentence-transformer-model

CMD ["python3", "db_seed.py"]
