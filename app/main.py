
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(title="PARS WMS CORE")

app.add_middleware(
    SessionMiddleware,
    secret_key="pars-wms-secret"
)

@app.get("/")
def home():
    return {"status": "ok"}
