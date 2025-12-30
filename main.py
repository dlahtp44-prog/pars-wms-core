from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db import init_db
from app.pages import index, inbound_page, outbound_page, move_page, inventory_page, history_page, calendar_month_page, admin_page, mobile_home, korean_redirects, qr_page, download
from app.routers import inbound_api, outbound_api, move_api, inventory_api, history_api, calendar_api

app = FastAPI(title="PARS WMS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
def _startup():
    init_db()

# pages
app.include_router(index.router)
app.include_router(mobile_home.router)
app.include_router(qr_page.router)
app.include_router(download.router)
app.include_router(inbound_page.router)
app.include_router(outbound_page.router)
app.include_router(move_page.router)
app.include_router(inventory_page.router)
app.include_router(history_page.router)
app.include_router(calendar_month_page.router)
app.include_router(admin_page.router)

# korean shortcuts
app.include_router(korean_redirects.router)

# apis
app.include_router(inbound_api.router)
app.include_router(outbound_api.router)
app.include_router(move_api.router)
app.include_router(inventory_api.router)
app.include_router(history_api.router)
app.include_router(calendar_api.router)