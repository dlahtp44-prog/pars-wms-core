from fastapi import (
    FastAPI, Request, Form, HTTPException, Depends
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import date
from typing import Optional
import os

# DB 로직 임포트
from app.db import (
    init_db, add_move, search_inventory, 
    get_calendar_memos_for_month, upsert_calendar_memo, get_history
)

app = FastAPI(title="PARS WMS")

# 경로 설정: 현재 파일(main.py)의 위치를 기준으로 절대 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- 이동 로직 관련 ---

@app.get("/m/qr/move/select", response_class=HTMLResponse)
def mobile_qr_move_select(request: Request, from_location: str):
    from_location = from_location.strip().replace(" ", "")
    rows = search_inventory(location=from_location, item_code="")
    return templates.TemplateResponse("m/qr_move_select.html", {
        "request": request, 
        "from_location": from_location, 
        "rows": rows
    })

@app.get("/m/qr/move/to", response_class=HTMLResponse)
def mobile_qr_move_to(
    request: Request,
    from_location: str,
    item_code: str,
    item_name: str = "",
    lot: str = "",
    spec: str = "",
    qty: int = 0
):
    # 템플릿 파일 존재 여부 확인을 위해 명시적으로 호출
    try:
        return templates.TemplateResponse(
            "m/qr_move_to.html", # 이 파일이 templates/m/ 안에 있어야 함
            {
                "request": request,
                "from_location": from_location,
                "item_code": item_code,
                "item_name": item_name,
                "lot": lot,
                "spec": spec,
                "qty": qty,
            }
        )
    except Exception as e:
        print(f"Template Error: {e}")
        raise HTTPException(status_code=500, detail=f"Template not found: m/qr_move_to.html")

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
    from_location = from_location.strip().replace(" ", "")
    to_location = to_location.strip().replace(" ", "")

    # DB 이동 처리
    add_move(from_location, to_location, item_code, item_name, lot, spec, "", qty, "QR 이동")

    return templates.TemplateResponse(
        "m/qr_move_done.html",
        {
            "request": request,
            "from_location": from_location,
            "to_location": to_location,
            "item_code": item_code,
            "qty": qty
        }
    )
