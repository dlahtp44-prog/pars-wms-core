from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import date, datetime
from typing import Optional, List, Dict, Any
import os, uuid

from .db import (
    init_db, add_inbound, add_outbound, add_move,
    search_inventory, get_history, upsert_calendar_memo,
    get_calendar_memos_for_month, get_calendar_memos_for_day,
    inventory_to_xlsx, history_to_xlsx,
    parse_inbound_xlsx, parse_outbound_xlsx, parse_move_xlsx
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(title="PARS WMS")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
# =========================
# Mobile Routes (QR only on mobile)
# =========================
@app.get("/m", response_class=HTMLResponse)
def mobile_menu(request: Request):
    return templates.TemplateResponse("mobile_menu.html", {"request": request})

@app.get("/m/qr", response_class=HTMLResponse)
def mobile_qr(request: Request):
    return templates.TemplateResponse("mobile/qr_scan.html", {"request": request})

@app.get("/api/qr/inventory")
def api_qr_inventory(location: str = ""):
    rows = search_inventory(location=location, item_code="")
    return {"count": len(rows), "items": rows}


# in-memory download store (token -> file path)
app.state.downloads = {}

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ---------- PAGES ----------
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
    return templates.TemplateResponse("inventory.html", {
        "request": request, "rows": rows, "location": location, "item_code": item_code
    })

@app.get("/page/history", response_class=HTMLResponse)
def page_history(request: Request, limit: int = 200):
    rows = get_history(limit=limit)
    return templates.TemplateResponse("history.html", {
        "request": request, "rows": rows, "limit": limit
    })

# ---------- Calendar (monthly memo) ----------
@app.get("/page/calendar/month", response_class=HTMLResponse)
def calendar_month(request: Request, year: int = date.today().year, month: int = date.today().month):
    memos = get_calendar_memos_for_month(year=year, month=month)
    # memos: { 'YYYY-MM-DD': [ {author, memo, created_at}, ... ] }
    today_s = date.today().isoformat()
    return templates.TemplateResponse("calendar_month.html", {
        "request": request,
        "year": year,
        "month": month,
        "memos": memos,
        "today": today_s
    })

@app.post("/page/calendar/memo")
def calendar_add_memo(
    request: Request,
    memo_date: str = Form(...),
    author: str = Form(""),
    memo: str = Form(...),
):
    # validate date format
    try:
        _ = date.fromisoformat(memo_date)
    except Exception:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다(YYYY-MM-DD).")
    upsert_calendar_memo(memo_date=memo_date, author=author.strip(), memo=memo.strip())
    # redirect back to that month
    y, m, _d = memo_date.split("-")
    return RedirectResponse(url=f"/page/calendar/month?year={int(y)}&month={int(m)}", status_code=303)

# ---------- Manual forms (DB) ----------
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

# ---------- Excel upload (pages) ----------
def _save_download_bytes(ext: str, data: bytes) -> str:
    token = uuid.uuid4().hex
    out_path = os.path.join("/tmp", f"download_{token}.{ext}")
    with open(out_path, "wb") as f:
        f.write(data)
    app.state.downloads[token] = out_path
    return token

@app.get("/download/{token}")
def download(token: str):
    path = app.state.downloads.get(token)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="다운로드 파일이 만료되었거나 존재하지 않습니다.")
    filename = os.path.basename(path)
    return FileResponse(path, filename=filename)

@app.post("/page/inbound/excel", response_class=HTMLResponse)
async def page_inbound_excel(request: Request, file: UploadFile = File(...)):
    report = await parse_inbound_xlsx(file)
    token = None
    if report.get("error_xlsx_bytes"):
        token = _save_download_bytes("xlsx", report["error_xlsx_bytes"])
    return templates.TemplateResponse("excel_result.html", {
        "request": request, "title": "입고 엑셀 업로드 결과", "report": report, "download_token": token,
        "back_url": "/page/inbound"
    })

@app.post("/page/outbound/excel", response_class=HTMLResponse)
async def page_outbound_excel(request: Request, file: UploadFile = File(...)):
    report = await parse_outbound_xlsx(file)
    token = None
    if report.get("error_xlsx_bytes"):
        token = _save_download_bytes("xlsx", report["error_xlsx_bytes"])
    return templates.TemplateResponse("excel_result.html", {
        "request": request, "title": "출고 엑셀 업로드 결과", "report": report, "download_token": token,
        "back_url": "/page/outbound"
    })

@app.post("/page/move/excel", response_class=HTMLResponse)
async def page_move_excel(request: Request, file: UploadFile = File(...)):
    report = await parse_move_xlsx(file)
    token = None
    if report.get("error_xlsx_bytes"):
        token = _save_download_bytes("xlsx", report["error_xlsx_bytes"])
    return templates.TemplateResponse("excel_result.html", {
        "request": request, "title": "이동 엑셀 업로드 결과", "report": report, "download_token": token,
        "back_url": "/page/move"
    })

# ---------- Excel download ----------
@app.get("/page/inventory.xlsx")
def inventory_xlsx(location: str = "", item_code: str = ""):
    rows = search_inventory(location=location, item_code=item_code)
    xbytes = inventory_to_xlsx(rows)
    token = _save_download_bytes("xlsx", xbytes)
    return RedirectResponse(url=f"/download/{token}", status_code=302)

@app.get("/page/history.xlsx")
def history_xlsx(limit: int = 200):
    rows = get_history(limit=limit)
    xbytes = history_to_xlsx(rows)
    token = _save_download_bytes("xlsx", xbytes)
    return RedirectResponse(url=f"/download/{token}", status_code=302)
