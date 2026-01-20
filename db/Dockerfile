# Name pbl-db-init
FROM python:alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY load_db.py .
# Would be a good idea to not copy at build time, but mount at runtime
COPY migrations ./migrations
COPY *.parquet ./

CMD ["python", "load_db.py"]
