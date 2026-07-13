FROM python:3.11-slim

WORKDIR /app

COPY backend/shared/ /app/shared/
COPY backend/ai-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ai-service/ /app/
COPY ai-engine/datasets/processed/ /app/datasets/processed/
COPY ai-engine/vector_database/ /app/vector_database/

ENV PYTHONPATH=/app:/app/shared

EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
