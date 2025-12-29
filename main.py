
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db import init_db

from app.routers import inbound, inventory, history

app = FastAPI(title="PARS WMS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(inbound.router)
app.include_router(inventory.router)
app.include_router(history.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
