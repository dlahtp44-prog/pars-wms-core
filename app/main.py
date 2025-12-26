from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db import init_db

# =====================================================
# ▶ API 라우터
# =====================================================
from app.routers import inbound, outbound, move, inventory, history

# =====================================================
# ▶ 페이지(UI) 라우터
# =====================================================
from app.pages import (
    index,
    inbound as inbound_page,
    outbound as outbound_page,
    move as move_page,
    inventory as inventory_page,
    history as history_page,
    excel_inbound
)

# =====================================================
# ▶ FastAPI 앱 생성
# =====================================================
app = FastAPI(
    title="PARS WMS CORE",
    version="1.0.0"
)

# =====================================================
# ▶ 템플릿 설정
# =====================================================
templates = Jinja2Templates(directory="app/templates")

# =====================================================
# ▶ CORS
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# ▶ 서버 시작 시 DB 초기화
# =====================================================
@app.on_event("startup")
def on_startup():
    init_db()

# =====================================================
# 🏠 메인 허브
# =====================================================
app.include_router(index.router)

# =====================================================
# 📄 페이지 라우터
# =====================================================
app.include_router(inbound_page.router)     # /입고
app.include_router(outbound_page.router)    # /출고
app.include_router(move_page.router)        # /이동
app.include_router(inventory_page.router)   # /재고
app.include_router(history_page.router)     # /이력
app.include_router(excel_inbound.router)    # /엑셀-입고

# =====================================================
# ✅ API 라우터
# =====================================================
app.include_router(inbound.router)
app.include_router(outbound.router)
app.include_router(move.router)
app.include_router(inventory.router)
app.include_router(history.router)
