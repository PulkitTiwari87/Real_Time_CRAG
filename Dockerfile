# Phase 15: containerized API. Build/run locally to verify:
# docker build -t rag-api . && docker run -p 8000:8000 --env-file .env rag-api
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY frontend/ frontend/
COPY config/ config/

# Persisted embedded-Qdrant storage; mount a volume here for real persistence.
RUN mkdir -p /app/local_vector_store \
    && useradd --create-home --shell /usr/sbin/nologin app \
    && chown -R app:app /app
VOLUME ["/app/local_vector_store"]
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["python", "-m", "uvicorn", "api.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
