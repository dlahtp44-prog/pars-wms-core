from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.paths import STATIC_DIR, TEMPLATES_DIR
from app.db import init_db

# Page routers
from app.pages.inbound_page import router as inbound_page_router
from app.pages.outbound_page import router as outbound_page_router
from app.pages.move_page import router as move_page_router
from app.pages.inventory_page import router as inventory_page_router
from app.pages.history_page import router as history_page_router
from app.pages.calendar_month_page import router as calendar_month_page_router
from app.pages.admin_page import router as admin_page_router
from app.pages.download_page import router as download_page_router
from app.pages.qr_mobile import router as mobile_qr_router

# API routers (JSON endpoints)
from app.routers.api_inbound import router as api_inbound_router
from app.routers.api_outbound import router as api_outbound_router
from app.routers.api_move import router as api_move_router
from app.routers.api_inventory import router as api_inventory_router
from app.routers.api_history import router as api_history_router

app = FastAPI(title="PARS WMS", version="1.0.0")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.on_event("startup")
def _startup():
    # Ensure DB schema exists
    init_db()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "PARS WMS"})

# Mobile home (simple menu)
@app.get("/m", response_class=HTMLResponse)
def mobile_home(request: Request):
    # template exists at templates/m/home.html
    return templates.TemplateResponse("m/home.html", {"request": request, "title": "PARS WMS (Mobile)"})

# Include page routers
app.include_router(inbound_page_router)
app.include_router(outbound_page_router)
app.include_router(move_page_router)
app.include_router(inventory_page_router)
app.include_router(history_page_router)
app.include_router(calendar_month_page_router)
app.include_router(admin_page_router)
app.include_router(download_page_router)
app.include_router(mobile_qr_router)

# Include API routers
app.include_router(api_inbound_router)
app.include_router(api_outbound_router)
app.include_router(api_move_router)
app.include_router(api_inventory_router)
app.include_router(api_history_router)
