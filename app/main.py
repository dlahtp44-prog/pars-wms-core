from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routers import inbound, inventory, history
from app.pages import inbound_page, inventory_page, history_page

app = FastAPI(title="PARS WMS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

@app.get("/")
def root():
    return RedirectResponse("/page/inbound")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# pages
app.include_router(inbound_page.router)
app.include_router(inventory_page.router)
app.include_router(history_page.router)

# apis
app.include_router(inbound.router)
app.include_router(inventory.router)
app.include_router(history.router)