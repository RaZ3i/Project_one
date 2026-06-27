# Multi-stage build: React frontend + FastAPI backend (build context = repo root)
FROM node:20-alpine AS frontend-build
ARG RAILWAY_GIT_COMMIT_SHA=local
ARG CACHEBUST=1
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN echo "cachebust=${CACHEBUST} commit=${RAILWAY_GIT_COMMIT_SHA}" && \
    VITE_BUILD_ID="${RAILWAY_GIT_COMMIT_SHA}" npm run build

FROM python:3.12-slim
ARG RAILWAY_GIT_COMMIT_SHA=local
ENV BUILD_ID=${RAILWAY_GIT_COMMIT_SHA}
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY --from=frontend-build /app/backend/static ./static

ENV PYTHONPATH=/app
EXPOSE 8000

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
