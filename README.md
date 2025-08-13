# SAFC-FINN - A Semi-automated Fact-Checking System for Finnish News

SAFC-FINN is a semi-automated fact-checking system for Finnish news. The system orchestrates multiple microservices, each performing fact-checking subtasks such as claim detection and evidence retrieval. The system also contains a monitoring service for tracking the quality of fact-checking task outputs.

## Overview

The SAFC-FINN follows this system design:

![SAFC-FINN Functional View](./DIME%20GPT%20-%20Functional%20View%28New%29.jpg)

The system is containerized with Docker Compose.

### Repository layout

- `docker-compose.yml`: Root compose file with all services via `extends`
- `nginx.conf`: TLS reverse proxy to `api`
- `api_service/`: routes requests to fact-checking tasks
- `claim_detection/`: orchestrates claim detection tasks; gets/updates labels, writes annotations
- `model_inference_service/`: generates claim model inference labels
- `evidence_retrieval/`: semantic search backed by Milvus and web search
- `milvus_standalone/`: Milvus + MinIO + etcd + optional DB seed job
- `web_scrape/`: searches fact-checking sites (FullFact, FactCheck.org, PolitiFact) for a claim
- `model_monitoring_service/`: monitors claim detection (F1, accuracy, recall) and semantic search (re-rank score, cosine similarity)
- `rabbitmq_server/`: manages message queue and RPC
- `helm`: contains Helm charts for deploying services to a Kubernetes cluster
- `workflow_service/`: deprecated

## Prerequisites

- Docker and Docker Compose
- Claim detection model located in `$MODEL_DIR`
- Milvus seed data at `$DATA_DIR` and `$FACEPAGER_DATA`

## Environment variables

Copy `.env.sample` files, rename them to `.env`, and update values inside each file. These files contain environment variables referenced by the system and its microservices.

## Deployment

1) Create required files
- Copy `.env.sample` files to `.env` and update values
- Ensure TLS certs/keys exist on the host under `/etc/ssl` (paths used by `nginx.conf`)
- Create basic-auth credentials for Nginx (first time):
  ```bash
  # macOS (Homebrew)
  brew install httpd
  htpasswd -c ./auth/.htpasswd admin
  ```

2) Start the services from the repository root
```bash
docker compose up -d
```

3) Verify services and set up authentication

First, generate a random API key and add it to the Postgres database:
```bash
KEY=$(openssl rand -hex 32); echo "$KEY"
docker compose exec api python -m app.api_key_tools ADD "$KEY"
```

Access the API docs:
- Via Nginx (requires basic auth): https://localhost/docs (443)
- Direct API (bypasses Nginx): http://localhost:8080/docs

In the docs, click “Authorize” and provide the header `x-api-key` with the value `$KEY`.

4) Stop
```bash
docker compose down
# or to also remove volumes:
# docker compose down -v
```

## License

See `LICENSE` for details. 