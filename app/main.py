from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db import init_db

from app.pages import home, inbound, outbound, move, inventory, history, qr, prints, calendar
from app.routers import api_inbound, api_outbound, api_move, api_inventory, api_history

app = FastAPI(title="PARS WMS CORE V3", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
def startup():
    init_db()

for r in [home, inbound, outbound, move, inventory, history, qr, prints, calendar]:
    app.include_router(r.router)

for r in [api_inbound, api_outbound, api_move, api_inventory, api_history]:
    app.include_router(r.router)
