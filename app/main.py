from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db

# API routers
from app.routers import inbound, outbound, move, inventory, history

# UI/page routers
from app.pages import (
    index,
    inbound as inbound_page,
    outbound as outbound_page,
    move as move_page,
    inventory as inventory_page,
    history as history_page,
    excel_inbound,
    excel_outbound,
    excel_move,
    download,
)

app = FastAPI(title="PARS WMS CORE", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

# UI
app.include_router(index.router)
app.include_router(inbound_page.router)
app.include_router(outbound_page.router)
app.include_router(move_page.router)
app.include_router(inventory_page.router)
app.include_router(history_page.router)

# Excel UI (Admin-only via HTTP Basic)
app.include_router(excel_inbound.router)
app.include_router(excel_outbound.router)
app.include_router(excel_move.router)

# Failed rows download
app.include_router(download.router)

# API
app.include_router(inbound.router)
app.include_router(outbound.router)
app.include_router(move.router)
app.include_router(inventory.router)
app.include_router(history.router)
