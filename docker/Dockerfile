# Usar Python 3.11 como base
FROM python:3.11-slim

WORKDIR /app

COPY src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

RUN mkdir -p /app/data

CMD ["python", "webscraping.py"]
