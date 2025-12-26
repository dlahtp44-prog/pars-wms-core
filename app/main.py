from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db import init_db

# ================= API 라우터 =================
from app.routers import inbound, outbound, move, inventory, history

# ================= PAGE 라우터 =================
from app.pages import (
    inbound as inbound_page,
    outbound as outbound_page,
    move as move_page,
    inventory as inventory_page,
    history as history_page,
)

app = FastAPI(title="PARS WMS CORE", version="1.0.0")

templates = Jinja2Templates(directory="app/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

# 🏠 메인
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ================= PAGE 등록 =================
app.include_router(inbound_page.router)
app.include_router(outbound_page.router)
app.include_router(move_page.router)
app.include_router(inventory_page.router)
app.include_router(history_page.router)

# ================= API 등록 =================
app.include_router(inbound.router)
app.include_router(outbound.router)
app.include_router(move.router)
app.include_router(inventory.router)
app.include_router(history.router)
