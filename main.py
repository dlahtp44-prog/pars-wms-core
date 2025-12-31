from fastapi import (
    FastAPI, Request, Form, HTTPException, Depends
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import date
from typing import Optional
import os

# DB 로직 임포트 (기존 경로 유지)
from app.db import init_db, add_move, search_inventory, get_calendar_memos_for_month, upsert_calendar_memo, get_history

app = FastAPI(title="PARS WMS")

# 경로 설정 최적화
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- 이동 관련 로직 ---

@app.get("/m/qr/move/select", response_class=HTMLResponse)
def mobile_qr_move_select(request: Request, from_location: str):
    from_location = from_location.strip().replace(" ", "")
    rows = search_inventory(location=from_location, item_code="")
    return templates.TemplateResponse("m/qr_move_select.html", {"request": request, "from_location": from_location, "rows": rows})

@app.get("/m/qr/move/to", response_class=HTMLResponse)
def mobile_qr_move_to(
    request: Request,
    from_location: Optional[str] = None,
    item_code: Optional[str] = None,
    item_name: Optional[str] = None,
    lot: Optional[str] = None,
    spec: Optional[str] = None,
    qty: Optional[int] = None,
):
    # 필수 데이터가 누락된 경우 안전하게 리다이렉트
    if not from_location or not item_code:
        return RedirectResponse(url="/m/qr/move", status_code=302)

    # 템플릿 파일 호출 (m/qr_move_to.html)
    return templates.TemplateResponse(
        "m/qr_move_to.html",
        {
            "request": request,
            "from_location": from_location,
            "item_code": item_code,
            "item_name": item_name or "",
            "lot": lot or "",
            "spec": spec or "",
            "qty": qty or 0,
        }
    )

@app.post("/m/qr/move/execute", response_class=HTMLResponse)
def mobile_qr_move_execute(
    request: Request,
    from_location: str = Form(...),
    to_location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(""),
    lot: str = Form(""),
    spec: str = Form(""),
    qty: int = Form(...),
):
    add_move(from_location, to_location, item_code, item_name, lot, spec, "", qty, "QR 이동")
    return templates.TemplateResponse("m/qr_move_done.html", locals())
