# main.py
# =========================================================
# PARS WMS CORE - Clean, stable skeleton
# =========================================================
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import init_db

# API Routers
from app.routers import inbound, outbound, move, inventory, history, report

# Page Routers
from app.pages import (
    index_page,
    inbound_page,
    outbound_page,
    move_page,
    inventory_page,
    history_page,
    report_page,
    qr_move_page,
    qr_location_page,
    qr_outbound_page,
)

app = FastAPI(title="PARS WMS CORE")

# Static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
def startup():
    init_db()

# API
app.include_router(inbound.router)
app.include_router(outbound.router)
app.include_router(move.router)
app.include_router(inventory.router)
app.include_router(history.router)
app.include_router(report.router)

# Pages
app.include_router(index_page.router)
app.include_router(inbound_page.router)
app.include_router(outbound_page.router)
app.include_router(move_page.router)
app.include_router(inventory_page.router)
app.include_router(history_page.router)
app.include_router(report_page.router)

# QR Pages
app.include_router(qr_move_page.router)
app.include_router(qr_location_page.router)
app.include_router(qr_outbound_page.router)
