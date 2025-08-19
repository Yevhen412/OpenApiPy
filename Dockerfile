FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements-prod.txt .
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements-prod.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["sh","-c","uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}"]
