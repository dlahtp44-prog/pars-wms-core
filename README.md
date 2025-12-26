# PARS WMS CORE (Clean Skeleton)

## Run locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Deploy (Railway)
- Repo root contains `main.py`
- Start command (if needed):
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```
