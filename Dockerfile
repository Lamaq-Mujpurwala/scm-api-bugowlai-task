# Production Dockerfile for Hugging Face Spaces
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./app /app/app
COPY ./alembic /alembic
COPY alembic.ini /

# Expose port
EXPOSE 8000

# Start the application directly (no entrypoint for HF Spaces)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
