from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.paths import STATIC_DIR

from app.db import init_db
from app.pages import (
    home, inbound_page, outbound_page, move_page,
    inventory_page, history_page,
    calendar_page, calendar_month_page,
    admin_page, download_page, qr_mobile
)
from app.routers import api_inbound, api_outbound, api_move

app = FastAPI(title="PARS WMS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Pages
app.include_router(home.router)
app.include_router(inbound_page.router)
app.include_router(outbound_page.router)
app.include_router(move_page.router)
app.include_router(inventory_page.router)
app.include_router(history_page.router)
app.include_router(calendar_page.router)
app.include_router(calendar_month_page.router)
app.include_router(admin_page.router)
app.include_router(download_page.router)
app.include_router(qr_mobile.router)

# APIs
app.include_router(api_inbound.router)
app.include_router(api_outbound.router)
app.include_router(api_move.router)
