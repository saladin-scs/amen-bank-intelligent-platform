# Amen Bank Intelligent Digital Banking Platform

Enterprise-grade internship platform for modern digital banking with an independent AI engine.

## Components

| Component | Technology | Description |
| --- | --- | --- |
| **Frontend** | Angular, Material, Tailwind | Public website + client area + AI assistant |
| **Backend** | FastAPI microservices | Gateway, Auth, Banking, AI inference API |
| **AI Engine** | Python, CRISP-DM | Knowledge base, embeddings, RAG, evaluation |

## Architecture

```text
                    Angular Frontend
                           |
                    API Gateway (:8000)
                           |
        -------------------------------------
        |                 |                 |
 Authentication     Banking Service     AI Service
   (:8001)              (:8002)           (:8003)
        |                 |                 |
    PostgreSQL       PostgreSQL        ChromaDB
        |                                   |
       Redis                          AI Engine Pipeline
```

The AI Engine is an **independent project** (`ai-engine/`). The backend AI service consumes artifacts it produces.

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 20+

### Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

| Service | URL |
| --- | --- |
| Frontend | http://localhost:4200 |
| API Gateway | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

### AI Engine Pipeline

```bash
cd ai-engine/preprocessing
pip install -r requirements.txt
python run_pipeline.py

cd ../embeddings
pip install -r requirements.txt
python build_index.py

cd ../evaluation
python evaluate_retrieval.py
```

## Repository Structure

```text
AmenBank-Platform/
├── frontend/                 # Angular application
├── backend/
│   ├── gateway/
│   ├── auth-service/
│   ├── banking-service/
│   ├── ai-service/
│   └── shared/
├── ai-engine/
│   ├── notebooks/
│   ├── datasets/
│   ├── preprocessing/
│   ├── embeddings/
│   ├── vector_database/
│   ├── evaluation/
│   ├── models/
│   └── deployment/
├── infrastructure/
│   ├── docker/
│   ├── nginx/
│   └── scripts/
├── docs/
├── .github/workflows/
├── docker-compose.yml
└── README.md
```

## Development Phases

| Phase | Status |
| --- | --- |
| 0 — Project initialization | Completed |
| 1 — AI dataset creation | Completed |
| 2 — CRISP-DM notebooks & embeddings | Completed |
| 3 — Backend microservices | Completed |
| 4 — Angular frontend | Completed |
| 5 — AI service integration | Completed |
| 6 — Testing | Completed |
| 7 — Deployment | Completed |

## Documentation

- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Database Schema](docs/database.md)
- [AI Pipeline](docs/ai-pipeline.md)
- [Deployment](docs/deployment.md)
- [Installation](docs/installation.md)

## Security

- JWT authentication with refresh tokens
- bcrypt password hashing
- CORS configuration
- Input validation (Pydantic v2)
- No secrets in source control — use `.env`

## Git Workflow

```text
main → develop → feature/*
```

Commit convention: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`

## License

Proprietary — Amen Bank internship project.
