# Phase 15: containerized API. Not verified in this sandbox -- no Docker
# available here (confirmed repeatedly this session). Build/run locally to
# verify: docker build -t rag-api . && docker run -p 8000:8000 --env-file .env rag-api
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY frontend/ frontend/
COPY config/ config/

# Persisted embedded-Qdrant storage; mount a volume here for real persistence.
VOLUME ["/app/local_vector_store"]

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
