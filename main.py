# main.py
from fastapi import FastAPI

app = FastAPI(title="PARS WMS CORE")

@app.get("/")
def root():
    return {"status": "PARS WMS CORE OK"}
