# Installation Guide

## Prerequisites

| Tool | Version | Purpose |
| --- | --- | --- |
| Python | 3.11+ | Backend + AI Engine |
| Node.js | 20+ | Angular frontend |
| Docker | 24+ | Container orchestration |
| Docker Compose | 2+ | Multi-service deployment |
| Git | 2.40+ | Version control |

## Clone Repository

```bash
git clone <repository-url>
cd AmenBank-Platform
git checkout develop
```

## Environment Setup

```bash
cp .env.example .env
```

Edit `.env` with your local values. Minimum required:

- `POSTGRES_PASSWORD`
- `JWT_SECRET_KEY`

## Option A: Full Docker Setup

```bash
docker compose up --build
```

## Option B: Local Development

### 1. PostgreSQL & Redis

```bash
docker compose up postgres redis chromadb -d
```

### 2. AI Engine

```bash
cd ai-engine/preprocessing
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python run_pipeline.py
pytest test_pipeline.py

cd ../embeddings
pip install -r requirements.txt
python build_index.py
```

### 3. Backend Services

Each service runs independently:

```bash
# Auth Service
cd backend/auth-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Banking Service
cd backend/banking-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002

# AI Service
cd backend/ai-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003

# Gateway
cd backend/gateway
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend

```bash
cd frontend
npm install
npm start
```

Open http://localhost:4200

## Verify Installation

```bash
# Health checks
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health

# Register a test user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!","full_name":"Test User"}'

# AI chat
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Quels services digitaux propose Amen Bank?","language":"fr"}'
```

## Running Tests

```bash
# AI preprocessing
cd ai-engine/preprocessing && pytest test_pipeline.py -v

# Backend (per service)
cd backend/auth-service && pytest tests/ -v
cd backend/banking-service && pytest tests/ -v
cd backend/ai-service && pytest tests/ -v
cd backend/gateway && pytest tests/ -v

# Frontend
cd frontend && npm test
```

## Troubleshooting

| Issue | Solution |
| --- | --- |
| Port already in use | Change ports in docker-compose.yml or stop conflicting services |
| ChromaDB connection failed | Ensure chromadb container is running on port 8100 |
| JWT errors | Verify `JWT_SECRET_KEY` matches across gateway and auth-service |
| Frontend CORS errors | Check `CORS_ORIGINS` includes `http://localhost:4200` |
| Embedding model download slow | First run downloads ~400MB model; be patient |

## IDE Setup

Recommended VS Code / Cursor extensions:

- Python (Pylance)
- Angular Language Service
- Docker
- REST Client
