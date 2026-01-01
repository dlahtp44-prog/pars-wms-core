
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db import init_db

from app.routers import inbound, outbound, move
from app.pages import (
    index_page, inbound_page, outbound_page, move_page,
    inventory_page, history_page
)

app = FastAPI(title="PARS WMS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

init_db()

# API
app.include_router(inbound.router)
app.include_router(outbound.router)
app.include_router(move.router)

# PAGE
app.include_router(index_page.router)
app.include_router(inbound_page.router)
app.include_router(outbound_page.router)
app.include_router(move_page.router)
app.include_router(inventory_page.router)
app.include_router(history_page.router)
