FROM python:3.12-slim-bullseye

WORKDIR /app

COPY requirements.txt .

# Install necessary system packages, including g++
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -U pip setuptools wheel
RUN pip install grpcio-tools
RUN pip install --no-cache-dir -r requirements.txt

COPY ./database /app
COPY .env .

EXPOSE 8091

CMD ["python", "seed.py"]
