FROM python:3.12.8-slim

WORKDIR /app

COPY requirements.txt .

# Install necessary system packages, including g++
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -U pip setuptools wheel
RUN pip install grpcio-tools
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app
COPY .env .
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENV PYTHONPATH="${PYTHONPATH}:/app/" \
    HF_HOME=/app/.cache/huggingface \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

USER appuser

# RUN python database/seed.py --test 1

EXPOSE 8091

CMD ["/app/docker-entrypoint.sh"]
