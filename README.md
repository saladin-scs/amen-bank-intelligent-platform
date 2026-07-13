<<<<<<< HEAD
# Amen Bank Intelligent Digital Banking Platform

Enterprise internship platform composed of three independent parts:

1. **Frontend** — Angular digital banking web platform
2. **Backend** — FastAPI microservices (gateway, auth, banking, AI inference API)
3. **AI Engine** — standalone CRISP-DM project (datasets, notebooks, vector DB, evaluation)

## Current phase completed

**AI Engine — Data Preparation (Knowledge Base Dataset)**

See [`ai-engine/datasets/README.md`](ai-engine/datasets/README.md).

```bash
cd ai-engine/preprocessing
pip install -r requirements.txt
python run_pipeline.py
```

## Target architecture

```text
Frontend → API Gateway → Auth / Banking / AI services
                ↓
         PostgreSQL / Redis / ChromaDB
```

The AI Engine lifecycle remains outside the backend and produces artifacts the AI service consumes.

## Workspace

```text
AmenBank-Platform/
  frontend/
  backend/
  ai-engine/
  infrastructure/
  docs/
  .github/
```

Subsequent phases will implement frontend, microservices, notebooks, and DevOps after this knowledge-base foundation is validated.
=======
amen-bank-intelligent-platform/

│
├── frontend/                 # Angular application
│
├── backend/                  # FastAPI Microservices
│   │
│   ├── gateway/
│   ├── auth-service/
│   ├── banking-service/
│   ├── ai-service/
│   └── shared/
│
├── ai-engine/                # AI development project
│   │
│   ├── notebooks/
│   ├── datasets/
│   ├── preprocessing/
│   ├── embeddings/
│   ├── evaluation/
│   └── models/
│
├── infrastructure/
│   │
│   ├── docker/
│   ├── nginx/
│   └── scripts/
│
├── docs/
│
├── .github/
│   └── workflows/
│
├── docker-compose.yml
│
├── README.md
│
├── .gitignore
│
└── LICENSE
>>>>>>> db684539f79c3a769df1c417e15142753b716f4b
