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
    excel_outbound,
    excel_move,
)

# ================= FastAPI 앱 생성 =================
app = FastAPI(
    title="PARS WMS CORE",
    version="1.0.0"
)

# ================= 템플릿 =================
templates = Jinja2Templates(directory="app/templates")

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= Startup =================
@app.on_event("startup")
def on_startup():
    init_db()

# ================= 메인 허브 =================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ================= PAGE 라우터 등록 =================
app.include_router(inbound_page.router)      # /입고
app.include_router(outbound_page.router)     # /출고
app.include_router(move_page.router)         # /이동
app.include_router(inventory_page.router)    # /재고
app.include_router(history_page.router)      # /이력
app.include_router(excel_outbound.router)    # /엑셀-출고
app.include_router(excel_move.router)        # /엑셀-이동

# ================= API 라우터 등록 =================
app.include_router(inbound.router)
app.include_router(outbound.router)
app.include_router(move.router)
app.include_router(inventory.router)
app.include_router(history.router)
