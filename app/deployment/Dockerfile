# Production Dockerfile for Hugging Face Spaces (repo-scoped)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd -m -u 1000 user
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code (repo layout)
COPY --chown=user:user ./app /app
COPY --chown=user:user ./app/deployment/alembic /app/alembic
COPY --chown=user:user ./app/deployment/alembic.ini /app/

RUN mkdir /data && chown -R user:user /data
USER user

EXPOSE 7860
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
