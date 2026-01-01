from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import date, datetime
from typing import Optional
import os

from app.db import (
    init_db,
    add_inbound, add_outbound, add_move,
    search_inventory, get_history,
    upsert_calendar_memo, get_calendar_memos_for_month,
    inventory_to_xlsx, history_to_xlsx,
    parse_inbound_xlsx, parse_outbound_xlsx, parse_move_xlsx,
    add_manual_log, manual_to_xlsx,
    rollback_history
)

app = FastAPI(title="PARS WMS")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.on_event("startup")
def startup():
    init_db()

# =========================
# HOME
# =========================
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# =========================
# API (PC form submit)
# =========================
@app.post("/api/inbound")
def api_inbound(
    location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    qty: int = Form(...),
    brand: str = Form(""),
    note: str = Form("")
):
    add_inbound(location, item_code, item_name, lot, spec, brand, qty, note)
    return RedirectResponse("/page/inbound", status_code=303)

@app.post("/api/outbound")
def api_outbound(
    location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    qty: int = Form(...),
    brand: str = Form(""),
    note: str = Form("")
):
    add_outbound(location, item_code, item_name, lot, spec, brand, qty, note)
    return RedirectResponse("/page/outbound", status_code=303)

@app.post("/api/move")
def api_move(
    from_location: str = Form(...),
    to_location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    qty: int = Form(...),
    brand: str = Form(""),
    note: str = Form("")
):
    add_move(from_location, to_location, item_code, item_name, lot, spec, brand, qty, note)
    return RedirectResponse("/page/move", status_code=303)

# Rollback API (무제한)
@app.post("/api/rollback/{history_id}")
def api_rollback(history_id: int, reason: str = Form("")):
    rollback_history(history_id, reason or "")
    return RedirectResponse(f"/page/history", status_code=303)

# =========================
# DESKTOP PAGES
# =========================
@app.get("/page/inbound", response_class=HTMLResponse)
def page_inbound(request: Request):
    return templates.TemplateResponse("inbound.html", {"request": request})

@app.post("/page/inbound/excel")
async def page_inbound_excel(file: UploadFile = File(...)):
    parse_inbound_xlsx(file)
    return RedirectResponse("/page/inbound", status_code=303)

@app.get("/page/outbound", response_class=HTMLResponse)
def page_outbound(request: Request):
    return templates.TemplateResponse("outbound.html", {"request": request})

@app.post("/page/outbound/excel")
async def page_outbound_excel(file: UploadFile = File(...)):
    parse_outbound_xlsx(file)
    return RedirectResponse("/page/outbound", status_code=303)

@app.get("/page/move", response_class=HTMLResponse)
def page_move(request: Request):
    return templates.TemplateResponse("move.html", {"request": request})

@app.post("/page/move/excel")
async def page_move_excel(file: UploadFile = File(...)):
    parse_move_xlsx(file)
    return RedirectResponse("/page/move", status_code=303)

@app.get("/page/inventory", response_class=HTMLResponse)
def page_inventory(request: Request, location: str = "", item_code: str = "", year: Optional[int]=None, month: Optional[int]=None):
    rows = search_inventory(location, item_code, year=year, month=month)
    return templates.TemplateResponse("inventory.html", {
        "request": request,
        "rows": rows,
        "location": location,
        "item_code": item_code,
        "year": year or "",
        "month": month or ""
    })


@app.get("/page/inventory.xlsx")
def page_inventory_xlsx(location: str = "", item_code: str = "", year: Optional[int]=None, month: Optional[int]=None):
    rows = search_inventory(location, item_code, year=year, month=month)
    data = inventory_to_xlsx(rows)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="inventory.xlsx"'}
    )

@app.get("/page/history", response_class=HTMLResponse)
def page_history(request: Request, limit: int = 200, year: Optional[int]=None, month: Optional[int]=None, htype: str=""):
    rows = get_history(limit=limit, year=year, month=month, htype=htype)
    return templates.TemplateResponse("history.html", {
        "request": request,
        "rows": rows,
        "limit": limit,
        "year": year or "",
        "month": month or "",
        "htype": htype or ""
    })


@app.get("/page/history.xlsx")
def page_history_xlsx(limit: int = 5000, year: Optional[int]=None, month: Optional[int]=None, htype: str=""):
    rows = get_history(limit=limit, year=year, month=month, htype=htype)
    data = history_to_xlsx(rows)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="history.xlsx"'}
    )

# =========================
# MANUAL ENTRY (PC)
# =========================
@app.get("/page/manual-entry", response_class=HTMLResponse)
def page_manual_entry(request: Request, year: Optional[int]=None, month: Optional[int]=None):
    now=datetime.now()
    y = year if year is not None else now.year
    m = month if month is not None else now.month
    return templates.TemplateResponse("manual_entry.html", {"request": request, "year": y, "month": m})

@app.post("/page/manual-entry")
def post_manual_entry(
    책임구분: str = Form(...),
    유형: str = Form(...),
    상황: str = Form(...),
    기타내용: str = Form(""),
    등록일자: str = Form(""),
    파손일자: str = Form(""),
    담당자: str = Form(""),
    수량: int = Form(0),
    내용: str = Form("")
):
    # 기타가 아닐 때 기타내용 무시
    if 유형 != "기타" and 상황 != "기타":
        기타내용 = ""
    add_manual_log(책임구분, 유형, 상황, 기타내용, 등록일자, 파손일자, 담당자, 수량, 내용)
    return RedirectResponse("/page/manual-entry", status_code=303)


@app.get("/page/manual-entry.xlsx")
def manual_entry_xlsx(year: Optional[int]=None, month: Optional[int]=None):
    data = manual_to_xlsx(year, month)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="manual_entry.xlsx"'}
    )

# =========================
# CALENDAR
# =========================
@app.get("/page/calendar/month", response_class=HTMLResponse)
def page_calendar_month(request: Request, year: int = date.today().year, month: int = date.today().month):
    memos = get_calendar_memos_for_month(year, month)
    return templates.TemplateResponse("calendar_month.html", {"request": request, "year": year, "month": month, "memos": memos})

@app.post("/page/calendar/memo")
def post_calendar_memo(memo_date: str = Form(...), author: str = Form(""), memo: str = Form(...)):
    upsert_calendar_memo(memo_date, author, memo)
    y = int(memo_date.split("-")[0]); m = int(memo_date.split("-")[1])
    return RedirectResponse(f"/page/calendar/month?year={y}&month={m}", status_code=303)

# =========================
# MOBILE HOME + QR MOVE (기존 유지)
# =========================
@app.get("/m", response_class=HTMLResponse)
def mobile_home(request: Request):
    return templates.TemplateResponse("home_mobile.html", {"request": request})

@app.get("/m/qr", response_class=HTMLResponse)
def mobile_qr(request: Request):
    return templates.TemplateResponse("mobile_qr.html", {"request": request})

@app.get("/m/qr/move", response_class=HTMLResponse)
def mobile_qr_move(request: Request):
    return templates.TemplateResponse("qr_move.html", {"request": request})

@app.post("/m/qr/move/complete")
def mobile_qr_move_complete(
    from_location: str = Form(...),
    to_location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    qty: int = Form(...),
    brand: str = Form(""),
    note: str = Form("")
):
    add_move(from_location, to_location, item_code, item_name, lot, spec, brand, qty, note)
    return RedirectResponse("/m/qr/move", status_code=303)

# 모바일 롤백(무제한): history_id 직접 입력/전달용
@app.post("/m/rollback/{history_id}")
def mobile_rollback(history_id: int, reason: str = Form("")):
    rollback_history(history_id, reason or "")
    return RedirectResponse("/m", status_code=303)

# =========================
# ADMIN (PC 전용)
# =========================
def _ensure_pc(request: Request):
    ua = request.headers.get("user-agent","").lower()
    # 아주 단순 휴리스틱: 모바일에서 관리자 접근 차단
    if "mobile" in ua or "android" in ua or "iphone" in ua:
        raise HTTPException(status_code=403, detail="관리자/라벨 기능은 PC에서만 사용 가능합니다.")

@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    _ensure_pc(request)
    return templates.TemplateResponse("admin_menu.html", {"request": request})

@app.get("/admin/labels/product", response_class=HTMLResponse)
def admin_label_product(request: Request):
    _ensure_pc(request)
    return templates.TemplateResponse("label_product.html", {"request": request})

@app.get("/admin/labels/location", response_class=HTMLResponse)
def admin_label_location(request: Request):
    _ensure_pc(request)
    return templates.TemplateResponse("label_location.html", {"request": request})
