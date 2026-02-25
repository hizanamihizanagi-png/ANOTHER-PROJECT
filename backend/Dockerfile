FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies from root
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the backend code
COPY backend/ ./backend/

# Expose port
EXPOSE 8000

# Start command is managed by discord-compose or use default
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
