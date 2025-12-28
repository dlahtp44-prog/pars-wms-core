import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.db import init_db

# =========================
# App
# =========================
app = FastAPI(title="PARS WMS CORE", version="1.0.0")

# Session (관리자 로그인/권한용)
SECRET_KEY = os.getenv("SESSION_SECRET", "pars-wms-session-secret")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Static
# /static/style.css, /static/app.css 등
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Startup: DB init + (필요시) 컬럼 마이그레이션
@app.on_event("startup")
def on_startup():
    init_db()

# iOS / browser icon 요청(없어도 무방하지만 로그 깔끔하게)
@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

@app.get("/apple-touch-icon.png")
@app.get("/apple-touch-icon-precomposed.png")
def apple_touch():
    return Response(status_code=204)

# =========================
# Pages (UI)
# =========================
from app.pages import (
    index, home, inbound, outbound, move, inventory, history,
    excel_inbound, excel_outbound, excel_move,
    calendar, admin, login,
    mobile, mobile_inbound, mobile_outbound, mobile_move, mobile_qr,
    label_location, label_product,
    prints, print_inventory, print_history,
    qr, qr_location, qr_move,
    backup, download,
)

app.include_router(index.router)
app.include_router(home.router)
app.include_router(inbound.router)
app.include_router(outbound.router)
app.include_router(move.router)
app.include_router(inventory.router)
app.include_router(history.router)

app.include_router(excel_inbound.router)
app.include_router(excel_outbound.router)
app.include_router(excel_move.router)

app.include_router(calendar.router)
app.include_router(login.router)
app.include_router(admin.router)

app.include_router(mobile.router)
app.include_router(mobile_inbound.router)
app.include_router(mobile_outbound.router)
app.include_router(mobile_move.router)
app.include_router(mobile_qr.router)

app.include_router(label_location.router)
app.include_router(label_product.router)

app.include_router(prints.router)
app.include_router(print_inventory.router)
app.include_router(print_history.router)

app.include_router(qr.router)
app.include_router(qr_location.router)
app.include_router(qr_move.router)

app.include_router(backup.router)
app.include_router(download.router)

# =========================
# API Routers
# =========================
from app.routers import (
    api_inbound, api_outbound, api_move, api_inventory, api_history,
    auth, print as api_print,
    inbound as inbound_api_router,
    outbound as outbound_api_router,
    move as move_api_router,
    inventory as inventory_api_router,
    history as history_api_router,
    calendar as calendar_api_router,
    label as label_api_router,
    backup as backup_api_router,
)

# REST API (Form 기반 한글 필드 포함)
app.include_router(api_inbound.router)
app.include_router(api_outbound.router)
app.include_router(api_move.router)
app.include_router(api_inventory.router)
app.include_router(api_history.router)

# 기타 API/관리 라우터
app.include_router(auth.router)
app.include_router(api_print.router)
app.include_router(inbound_api_router.router)
app.include_router(outbound_api_router.router)
app.include_router(move_api_router.router)
app.include_router(inventory_api_router.router)
app.include_router(history_api_router.router)
app.include_router(calendar_api_router.router)
app.include_router(label_api_router.router)
app.include_router(backup_api_router.router)
