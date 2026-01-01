from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.paths import STATIC_DIR, TEMPLATES_DIR
from app.db import init_db

# API
from app.routers import inbound, move, outbound, location

# ADMIN
from app.auth import admin_required
from app.admin import location_admin, summary_admin

# PC PAGES
from app.pages import (
    home,
    inbound_page, outbound_page, move_page,
    inventory_page, history_page,
    calendar_month_page, calendar_page,
)

# MOBILE PAGES
from app.pages import (
    mobile_home,
    mobile_inbound,
    mobile_move,
    mobile_outbound,
    mobile_qr_page,
    mobile_qr_inventory,
)

app = FastAPI(title="PARS WMS v1.5 OPS FINAL")

# DB init/migration
init_db()

# templates/static
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.state.templates = templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# --------------------
# API routers
# --------------------
app.include_router(inbound.router)
app.include_router(outbound.router)
app.include_router(move.router)
app.include_router(location.router)

# --------------------
# PC page routers
# --------------------
app.include_router(home.router)
app.include_router(inbound_page.router)
app.include_router(outbound_page.router)
app.include_router(move_page.router)
app.include_router(inventory_page.router)
app.include_router(history_page.router)
app.include_router(calendar_page.router)
app.include_router(calendar_month_page.router)

# --------------------
# Mobile routers
# --------------------
app.include_router(mobile_home.router)
app.include_router(mobile_inbound.router)
app.include_router(mobile_move.router)
app.include_router(mobile_outbound.router)
app.include_router(mobile_qr_page.router)
app.include_router(mobile_qr_inventory.router)

# --------------------
# Admin routers (admin only)
# --------------------
app.include_router(location_admin.router, dependencies=[Depends(admin_required)])
app.include_router(summary_admin.router, dependencies=[Depends(admin_required)])
