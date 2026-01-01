from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.paths import STATIC_DIR, TEMPLATES_DIR
from app.db import init_db

# API routers (폼 저장)
from app.routers import api_inbound, outbound_api, move_api, inventory_api, history_api, location

# PC pages
from app.pages import home, inbound_page, outbound_page, move_page, inventory_page, history_page, calendar_month_page, calendar_page

# Mobile pages
from app.pages import mobile_home, qr_page, qr_mobile, qr_move, qr_location, qr_inventory

# Admin
from app.admin import location_admin, summary_admin
from app.auth import admin_required

app = FastAPI(title="PARS WMS v1.5 FIX FULLCHECK")

init_db()

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.state.templates = templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# API
app.include_router(api_inbound.router)
app.include_router(outbound_api.router)
app.include_router(move_api.router)
app.include_router(inventory_api.router)
app.include_router(history_api.router)
app.include_router(location.router)

# PC pages
app.include_router(home.router)
app.include_router(inbound_page.router)
app.include_router(outbound_page.router)
app.include_router(move_page.router)
app.include_router(inventory_page.router)
app.include_router(history_page.router)
app.include_router(calendar_page.router)
app.include_router(calendar_month_page.router)

# Mobile & QR pages
app.include_router(mobile_home.router)
app.include_router(qr_page.router)
app.include_router(qr_mobile.router)
app.include_router(qr_move.router)
app.include_router(qr_location.router)
app.include_router(qr_inventory.router)

# Admin (protected)
app.include_router(location_admin.router, dependencies=[Depends(admin_required)])
app.include_router(summary_admin.router, dependencies=[Depends(admin_required)])
