FROM python:3.11-slim

WORKDIR /app

COPY shared/ /app/shared/
COPY banking-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY banking-service/ /app/

ENV PYTHONPATH=/app:/app/shared

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
