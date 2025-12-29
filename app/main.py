
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db

# API routers
from app.routers import inbound, inventory, history

# Page routers
from app.pages import index_page, inbound_page, inventory_page, history_page

app = FastAPI(title="PARS WMS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

# ---------- Root ----------
@app.get("/")
def root():
    # Root should never 404; redirect to main page
    return RedirectResponse("/page/inbound")

# ---------- Static ----------
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ---------- Pages ----------
app.include_router(index_page.router)
app.include_router(inbound_page.router)
app.include_router(inventory_page.router)
app.include_router(history_page.router)

# ---------- APIs ----------
app.include_router(inbound.router)
app.include_router(inventory.router)
app.include_router(history.router)
