from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import init_db

from app.routers import inbound, outbound, move, inventory, history
from app.pages import index, inbound as inbound_page, outbound as outbound_page
from app.pages import move as move_page, inventory as inventory_page, history as history_page, qr as qr_page

app = FastAPI(title="PARS WMS (Korean Standard)")

init_db()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# API
app.include_router(inbound.router)
app.include_router(outbound.router)
app.include_router(move.router)
app.include_router(inventory.router)
app.include_router(history.router)

# Pages
app.include_router(index.router)
app.include_router(inbound_page.router)
app.include_router(outbound_page.router)
app.include_router(move_page.router)
app.include_router(inventory_page.router)
app.include_router(history_page.router)
app.include_router(qr_page.router)

