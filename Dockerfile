FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway sets PORT; JSON CMD won't expand env vars unless via shell.
CMD ["sh","-c","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
