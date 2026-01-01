FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps (for pillow/reportlab fonts etc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Render/railway will provide PORT
ENV PORT=8000
EXPOSE 8000

CMD ["bash","-lc","uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
