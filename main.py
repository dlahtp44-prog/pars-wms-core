from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.paths import STATIC_DIR, TEMPLATES_DIR
from app.db import init_db
from app.auth import admin_required

# API
from app.routers import inbound, outbound, move, inventory, history, location

# PC pages
from app.pages import (
    home,
    inbound_page,
    outbound_page,
    move_page,
    inventory_page,
    history_page,
    calendar_month_page,
    calendar_page,
)

# Mobile / QR pages (모바일 전용)
from app.pages.mobile import (
    home as mobile_home,
    qr_home,
    qr_move,
    qr_inventory,
)

# Admin
from app.admin import location_admin, summary_admin

app = FastAPI(title="PARS WMS v1.5 FINAL")

init_db()

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.state.templates = templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# API
app.include_router(inbound.router)
app.include_router(outbound.router)
app.include_router(move.router)
app.include_router(inventory.router)
app.include_router(history.router)
app.include_router(location.router)

# PC
app.include_router(home.router)
app.include_router(inbound_page.router)
app.include_router(outbound_page.router)
app.include_router(move_page.router)
app.include_router(inventory_page.router)
app.include_router(history_page.router)
app.include_router(calendar_month_page.router)
app.include_router(calendar_page.router)

# Mobile
app.include_router(mobile_home.router)

# Mobile QR
app.include_router(qr_home.router)
app.include_router(qr_move.router)
app.include_router(qr_inventory.router)

# Admin
app.include_router(
    location_admin.router,
    dependencies=[Depends(admin_required)]
)
app.include_router(
    summary_admin.router,
    dependencies=[Depends(admin_required)]
)
