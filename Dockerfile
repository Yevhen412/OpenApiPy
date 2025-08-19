FROM python:3.11-slim

WORKDIR /app

# УСТАНАВЛИВАЕМ git
RUN apt-get update && apt-get install -y git

COPY requirements-prod.txt requirements.txt
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
