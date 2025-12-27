
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.db import init_db

# API routers
from app.routers import api_inbound, api_history, inventory, move, outbound, label, print as print_router

# Page routers (PC)
from app.pages import (
    index, inbound, outbound as outbound_page, move as move_page,
    inventory as inventory_page, history as history_page,
    excel_inbound, excel_outbound, excel_move,
    admin, backup, calendar, login, mobile, mobile_inbound, mobile_outbound, mobile_move, mobile_qr,
    print_inventory, print_history
)
from app.pages import mobile_calendar  # newly added

app = FastAPI(title="PARS WMS CORE", version="1.0.0")

# Sessions for admin/auth helpers
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "pars-wms-secret-key"))

# CORS (필요 없으면 지워도 됨)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
def on_startup():
    init_db()

# -----------------
# Pages (PC)
# -----------------
app.include_router(index.router)
app.include_router(inbound.router)
app.include_router(outbound_page.router)
app.include_router(move_page.router)
app.include_router(inventory_page.router)
app.include_router(history_page.router)

app.include_router(excel_inbound.router)
app.include_router(excel_outbound.router)
app.include_router(excel_move.router)

app.include_router(calendar.router)
app.include_router(login.router)
app.include_router(admin.router)
app.include_router(backup.router)

app.include_router(print_inventory.router)
app.include_router(print_history.router)

# -----------------
# Mobile
# -----------------
app.include_router(mobile.router)               # /m
app.include_router(mobile_inbound.router)       # /m/입고
app.include_router(mobile_outbound.router)      # /m/출고
app.include_router(mobile_move.router)          # /m/이동
app.include_router(mobile_qr.router)            # /m/qr
app.include_router(mobile_calendar.router)      # /m/calendar

# -----------------
# API
# -----------------
app.include_router(api_inbound.router)          # /api/입고
app.include_router(outbound.router)             # /api/출고
app.include_router(move.router)                 # /api/이동
app.include_router(inventory.router)            # /api/재고
app.include_router(api_history.router)          # /api/이력

# Labels / prints (API endpoints)
app.include_router(label.router)                # /label/...
app.include_router(print_router.router)         # /print/...

