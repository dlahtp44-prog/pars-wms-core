from fastapi import FastAPI
from app.db import init_db

app = FastAPI(title="PARS WMS CORE")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"status": "PARS WMS CORE Online"}
