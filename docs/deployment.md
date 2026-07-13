# Deployment Guide

## Docker Compose (Recommended)

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env with secure passwords and API keys
```

### 2. Build AI index (first time)

```bash
cd ai-engine/preprocessing
pip install -r requirements.txt
python run_pipeline.py

cd ../embeddings
pip install -r requirements.txt
python build_index.py
```

### 3. Start all services

```bash
docker compose up --build -d
```

### 4. Verify health

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

### 5. Access

| Service | URL |
| --- | --- |
| Frontend | http://localhost:4200 |
| Nginx (unified) | http://localhost:80 |
| API Gateway | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| ChromaDB | http://localhost:8100 |

## Service Ports

| Service | Port |
| --- | --- |
| nginx | 80 |
| frontend | 4200 |
| gateway | 8000 |
| auth-service | 8001 |
| banking-service | 8002 |
| ai-service | 8003 |
| postgres | 5432 |
| redis | 6379 |
| chromadb | 8100 |

## Production Considerations

- Replace `JWT_SECRET_KEY` with a cryptographically random 256-bit key
- Use managed PostgreSQL (RDS, Cloud SQL)
- Enable HTTPS via reverse proxy / load balancer
- Set `LLM_PROVIDER=openai` with valid API key
- Configure log aggregation (ELK, Datadog)
- Set resource limits in docker-compose
- Enable PostgreSQL backups
- Use secrets manager for credentials

## Scaling

```yaml
# docker-compose.override.yml
services:
  banking-service:
    deploy:
      replicas: 3
  ai-service:
    deploy:
      replicas: 2
```

## Monitoring

Each service exposes:

- `GET /health` — liveness probe
- Structured JSON logging to stdout

## Database Migrations

```bash
# Auth service
docker exec amenbank-auth alembic upgrade head

# Banking service
docker exec amenbank-banking alembic upgrade head
```

## Stopping

```bash
docker compose down          # stop containers
docker compose down -v       # stop + remove volumes
```
