from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import date
import os, uuid

# =========================
# DB
# =========================
from app.db import (
    init_db, add_inbound, add_outbound, add_move,
    search_inventory, get_history, upsert_calendar_memo,
    get_calendar_memos_for_month,
    inventory_to_xlsx, history_to_xlsx,
    parse_inbound_xlsx, parse_outbound_xlsx, parse_move_xlsx
)

# =========================
# APP INIT (중요: 단 1번)
# =========================
app = FastAPI(title="PARS WMS")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# =========================
# QR 전용 Router / Page (추가)
# =========================
from app.pages import mobile_home, mobile_qr
from app.routers.qr_inventory import router as qr_inventory_router

app.include_router(mobile_home.router)
app.include_router(mobile_qr.router)
app.include_router(qr_inventory_router)

from app.pages import mobile_qr_inventory
app.include_router(mobile_qr_inventory.router)

@app.get("/m/qr/inventory", response_class=HTMLResponse)
def mobile_qr_inventory(request: Request, location: str):

    # 1️⃣ 기본 정리
    location = location.strip()

    # 2️⃣ 대소문자/공백/URL 인코딩 대비
    location = location.replace(" ", "")

    # 3️⃣ 부분검색 허용 (PC와 동일하게)
    rows = search_inventory(
        location=location,
        item_code=""
    )

    return templates.TemplateResponse(
        "mobile/qr_inventory.html",
        {
            "request": request,
            "location": location,
            "rows": rows
        }
    )


# =========================
# 상태 저장 (다운로드)
# =========================
app.state.downloads = {}

@app.on_event("startup")
def startup():
    init_db()

# =========================
# INDEX
# =========================
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# =========================
# PAGES
# =========================
@app.get("/page/inbound", response_class=HTMLResponse)
def page_inbound(request: Request):
    return templates.TemplateResponse("inbound.html", {"request": request})

@app.get("/page/outbound", response_class=HTMLResponse)
def page_outbound(request: Request):
    return templates.TemplateResponse("outbound.html", {"request": request})

@app.get("/page/move", response_class=HTMLResponse)
def page_move(request: Request):
    return templates.TemplateResponse("move.html", {"request": request})

@app.get("/page/inventory", response_class=HTMLResponse)
def page_inventory(request: Request, location: str = "", item_code: str = ""):
    rows = search_inventory(location=location, item_code=item_code)
    return templates.TemplateResponse(
        "inventory.html",
        {"request": request, "rows": rows, "location": location, "item_code": item_code}
    )

@app.get("/page/history", response_class=HTMLResponse)
def page_history(request: Request, limit: int = 200):
    rows = get_history(limit=limit)
    return templates.TemplateResponse(
        "history.html",
        {"request": request, "rows": rows, "limit": limit}
    )

# =========================
# CALENDAR
# =========================
@app.get("/page/calendar/month", response_class=HTMLResponse)
def calendar_month(request: Request, year: int = date.today().year, month: int = date.today().month):
    memos = get_calendar_memos_for_month(year, month)
    return templates.TemplateResponse(
        "calendar_month.html",
        {
            "request": request,
            "year": year,
            "month": month,
            "memos": memos,
            "today": date.today().isoformat()
        }
    )

@app.post("/page/calendar/memo")
def calendar_add_memo(
    memo_date: str = Form(...),
    author: str = Form(""),
    memo: str = Form(...)
):
    upsert_calendar_memo(memo_date, author.strip(), memo.strip())
    y, m, _ = memo_date.split("-")
    return RedirectResponse(
        url=f"/page/calendar/month?year={int(y)}&month={int(m)}",
        status_code=303
    )

# =========================
# API (기존 기능 그대로)
# =========================
@app.post("/api/inbound")
def api_inbound(
    location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    brand: str = Form(""),
    qty: int = Form(...),
    note: str = Form("")
):
    add_inbound(location, item_code, item_name, lot, spec, brand, qty, note)
    return {"ok": True}

@app.post("/api/outbound")
def api_outbound(
    location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    brand: str = Form(""),
    qty: int = Form(...),
    note: str = Form("")
):
    add_outbound(location, item_code, item_name, lot, spec, brand, qty, note)
    return {"ok": True}

@app.post("/api/move")
def api_move(
    from_location: str = Form(...),
    to_location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    brand: str = Form(""),
    qty: int = Form(...),
    note: str = Form("")
):
    add_move(from_location, to_location, item_code, item_name, lot, spec, brand, qty, note)
    return {"ok": True}

# =========================
# DOWNLOAD UTILS
# =========================
def _save_download(ext: str, data: bytes) -> str:
    token = uuid.uuid4().hex
    path = f"/tmp/download_{token}.{ext}"
    with open(path, "wb") as f:
        f.write(data)
    app.state.downloads[token] = path
    return token

@app.get("/download/{token}")
def download(token: str):
    path = app.state.downloads.get(token)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404)
    return FileResponse(path, filename=os.path.basename(path))

# =========================
# EXCEL UPLOAD
# =========================
@app.post("/page/inbound/excel", response_class=HTMLResponse)
async def inbound_excel(request: Request, file: UploadFile = File(...)):
    report = await parse_inbound_xlsx(file)
    token = _save_download("xlsx", report["error_xlsx_bytes"]) if report.get("error_xlsx_bytes") else None
    return templates.TemplateResponse(
        "excel_result.html",
        {"request": request, "title": "입고 엑셀 업로드 결과", "report": report, "download_token": token, "back_url": "/page/inbound"}
    )

@app.post("/page/outbound/excel", response_class=HTMLResponse)
async def outbound_excel(request: Request, file: UploadFile = File(...)):
    report = await parse_outbound_xlsx(file)
    token = _save_download("xlsx", report["error_xlsx_bytes"]) if report.get("error_xlsx_bytes") else None
    return templates.TemplateResponse(
        "excel_result.html",
        {"request": request, "title": "출고 엑셀 업로드 결과", "report": report, "download_token": token, "back_url": "/page/outbound"}
    )

@app.post("/page/move/excel", response_class=HTMLResponse)
async def move_excel(request: Request, file: UploadFile = File(...)):
    report = await parse_move_xlsx(file)
    token = _save_download("xlsx", report["error_xlsx_bytes"]) if report.get("error_xlsx_bytes") else None
    return templates.TemplateResponse(
        "excel_result.html",
        {"request": request, "title": "이동 엑셀 업로드 결과", "report": report, "download_token": token, "back_url": "/page/move"}
    )

# =========================
# EXCEL DOWNLOAD
# =========================
@app.get("/page/inventory.xlsx")
def inventory_xlsx(location: str = "", item_code: str = ""):
    token = _save_download("xlsx", inventory_to_xlsx(search_inventory(location, item_code)))
    return RedirectResponse(url=f"/download/{token}", status_code=302)

@app.get("/page/history.xlsx")
def history_xlsx(limit: int = 200):
    token = _save_download("xlsx", history_to_xlsx(get_history(limit)))
    return RedirectResponse(url=f"/download/{token}", status_code=302)
