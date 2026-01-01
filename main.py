from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# API routers
from app.routers import (
    inbound,
    outbound,
    move,
    inventory,
    history,
    location,
)

# PC pages
from app.pages import (
    home,
    inbound_page,
    outbound_page,
    move_page,
    inventory_page,
    history_page,
    calendar_page,
)

# Mobile / QR pages
from app.pages.mobile import (
    home as mobile_home,
    qr_home,
    qr_move,
    qr_inventory,
)

app = FastAPI(title="PARS WMS v1.6")

# templates / static (상대경로 고정)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# API
app.include_router(inbound.router)
app.include_router(outbound.router)
app.include_router(move.router)
app.include_router(inventory.router)
app.include_router(history.router)
app.include_router(location.router)

# PC pages
app.include_router(home.router)
app.include_router(inbound_page.router)
app.include_router(outbound_page.router)
app.include_router(move_page.router)
app.include_router(inventory_page.router)
app.include_router(history_page.router)
app.include_router(calendar_page.router)

# Mobile pages
app.include_router(mobile_home.router)
app.include_router(qr_home.router)
app.include_router(qr_move.router)
app.include_router(qr_inventory.router)
