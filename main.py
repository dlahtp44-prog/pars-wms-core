from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from zoneinfo import ZoneInfo
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "app", "templates")

from app.db import (
    init_db,
    add_inbound, add_outbound, add_move,
    parse_inbound_xlsx, parse_outbound_xlsx, parse_move_xlsx,
    search_inventory, get_history,
    inventory_to_xlsx, history_to_xlsx,
    upsert_calendar_memo, get_calendar_memos_for_month,
)

from app.core.downloads import create_token, pop_token

KST = ZoneInfo("Asia/Seoul")

app = FastAPI(title="PARS WMS v1.0")

# Static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.state.templates = templates

# DB init
init_db()

# -------------------------
# Download (in-memory token)
# -------------------------
@app.get("/download/{token}")
def download(token: str):
    item = pop_token(token)
    if not item:
        raise HTTPException(status_code=404, detail="다운로드 토큰이 없거나 만료되었습니다.")
    headers = {"Content-Disposition": f'attachment; filename="{item.filename}"'}
    return Response(content=item.data, media_type=item.content_type, headers=headers)

# -------------------------
# Home
# -------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    # existing template: home_combined.html
    return templates.TemplateResponse("home_combined.html", {"request": request})

# -------------------------
# Desktop Pages
# -------------------------
@app.get("/page/inbound", response_class=HTMLResponse)
def page_inbound(request: Request):
    return templates.TemplateResponse("inbound.html", {"request": request})

@app.get("/page/outbound", response_class=HTMLResponse)
def page_outbound(request: Request):
    return templates.TemplateResponse("outbound.html", {"request": request})

@app.get("/page/move", response_class=HTMLResponse)
def page_move(request: Request):
    return templates.TemplateResponse("move.html", {"request": request})

# Inventory page + xlsx download (keep legacy URL used by template)
@app.get("/page/inventory", response_class=HTMLResponse)
def page_inventory(request: Request, location: str = "", item_code: str = ""):
    rows = search_inventory(location=location, item_code=item_code)
    return templates.TemplateResponse(
        "inventory.html",
        {"request": request, "rows": rows, "location": location, "item_code": item_code},
    )

@app.get("/page/inventory.xlsx")
def page_inventory_xlsx(location: str = "", item_code: str = ""):
    rows = search_inventory(location=location, item_code=item_code)
    data = inventory_to_xlsx(rows)
    headers = {"Content-Disposition": 'attachment; filename="inventory.xlsx"'}
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )

# History page + xlsx download (keep legacy URL used by template)
@app.get("/page/history", response_class=HTMLResponse)
def page_history(request: Request, limit: int = 200):
    rows = get_history(limit=limit)
    return templates.TemplateResponse(
        "history.html", {"request": request, "rows": rows, "limit": limit}
    )

@app.get("/page/history.xlsx")
def page_history_xlsx(limit: int = 200):
    rows = get_history(limit=limit)
    data = history_to_xlsx(rows)
    headers = {"Content-Disposition": 'attachment; filename="history.xlsx"'}
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )

# -------------------------
# Calendar (month + memo)
# Template expects:
#   GET /page/calendar/month?year=YYYY&month=M
#   POST /page/calendar/memo
# -------------------------
@app.get("/page/calendar/month", response_class=HTMLResponse)
def calendar_month(request: Request, year: int = None, month: int = None):
    now = datetime.now(tz=KST)
    y = year or now.year
    m = month or now.month
    memos = get_calendar_memos_for_month(y, m)  # { "YYYY-MM-DD": [ ... ] }
    return templates.TemplateResponse(
        "calendar_month.html",
        {"request": request, "year": y, "month": m, "memos": memos, "today": now.strftime("%Y-%m-%d")},
    )

@app.post("/page/calendar/memo")
def calendar_memo(
    year: int = Form(...),
    month: int = Form(...),
    ymd: str = Form(...),
    memo: str = Form(...),
    author: str = Form(""),
):
    # upsert (same day + author)
    upsert_calendar_memo(ymd=ymd, author=author, memo=memo)
    return RedirectResponse(url=f"/page/calendar/month?year={year}&month={month}", status_code=303)

# -------------------------
# API: manual inbound/outbound/move (폼 저장)
# Required: location/item_code/item_name/lot/spec/qty
# -------------------------
def _req_nonempty(label: str, v: str) -> str:
    v = (v or "").strip()
    if not v:
        raise HTTPException(status_code=400, detail=f"{label} 값이 비어있습니다.")
    return v

@app.post("/api/inbound")
def api_inbound(
    location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    brand: str = Form(""),
    qty: int = Form(...),
    note: str = Form(""),
):
    location = _req_nonempty("로케이션", location)
    item_code = _req_nonempty("품번", item_code)
    item_name = _req_nonempty("품명", item_name)
    lot = _req_nonempty("LOT", lot)
    spec = _req_nonempty("규격", spec)
    if qty <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")
    add_inbound(location, item_code, item_name, lot, spec, (brand or "").strip(), qty, (note or "").strip())
    return RedirectResponse(url="/page/inbound", status_code=303)

@app.post("/api/outbound")
def api_outbound(
    location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    brand: str = Form(""),
    qty: int = Form(...),
    note: str = Form(""),
):
    location = _req_nonempty("로케이션", location)
    item_code = _req_nonempty("품번", item_code)
    item_name = _req_nonempty("품명", item_name)
    lot = _req_nonempty("LOT", lot)
    spec = _req_nonempty("규격", spec)
    if qty <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")
    add_outbound(location, item_code, item_name, lot, spec, (brand or "").strip(), qty, (note or "").strip())
    return RedirectResponse(url="/page/outbound", status_code=303)

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
    note: str = Form(""),
):
    from_location = _req_nonempty("출발 로케이션", from_location)
    to_location = _req_nonempty("도착 로케이션", to_location)
    item_code = _req_nonempty("품번", item_code)
    item_name = _req_nonempty("품명", item_name)
    lot = _req_nonempty("LOT", lot)
    spec = _req_nonempty("규격", spec)
    if qty <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")
    add_move(from_location, to_location, item_code, item_name, lot, spec, (brand or "").strip(), qty, (note or "").strip())
    return RedirectResponse(url="/page/move", status_code=303)

# -------------------------
# Excel Upload (page routes)
# Must match template actions:
#  /page/inbound/excel, /page/outbound/excel, /page/move/excel
# Returns excel_result.html
# -------------------------
def _report_from_parse(result: dict, title: str, retry_url: str, filename: str):
    ok = result.get("ok", 0)
    fail = result.get("fail", 0)
    errors = result.get("errors", [])
    token = None
    err_bytes = result.get("error_xlsx_bytes")
    if err_bytes:
        token = create_token(
            filename=filename,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            data=err_bytes,
            ttl_minutes=30,
        )
    return {
        "success": ok,
        "failed": fail,
        "errors": errors,
        "fail_token": token,
        "title": title,
        "retry_url": retry_url,
    }

@app.post("/page/inbound/excel", response_class=HTMLResponse)
async def page_inbound_excel(request: Request, file: UploadFile = File(...)):
    result = await parse_inbound_xlsx(file)
    report = _report_from_parse(result, "입고 엑셀 업로드 결과", "/page/inbound", "inbound_errors.xlsx")
    return templates.TemplateResponse("excel_result.html", {"request": request, "report": report})

@app.post("/page/outbound/excel", response_class=HTMLResponse)
async def page_outbound_excel(request: Request, file: UploadFile = File(...)):
    result = await parse_outbound_xlsx(file)
    report = _report_from_parse(result, "출고 엑셀 업로드 결과", "/page/outbound", "outbound_errors.xlsx")
    return templates.TemplateResponse("excel_result.html", {"request": request, "report": report})

@app.post("/page/move/excel", response_class=HTMLResponse)
async def page_move_excel(request: Request, file: UploadFile = File(...)):
    result = await parse_move_xlsx(file)
    report = _report_from_parse(result, "이동 엑셀 업로드 결과", "/page/move", "move_errors.xlsx")
    return templates.TemplateResponse("excel_result.html", {"request": request, "report": report})

# -------------------------
# Mobile
# -------------------------
@app.get("/m", response_class=HTMLResponse)
def mobile_home(request: Request):
    return templates.TemplateResponse("m/home.html", {"request": request})

@app.get("/m/qr", response_class=HTMLResponse)
def mobile_qr_home(request: Request):
    return templates.TemplateResponse("m/qr.html", {"request": request})

# 1) scan from location
@app.get("/m/qr/move/from", response_class=HTMLResponse)
def mobile_qr_move_from(request: Request):
    return templates.TemplateResponse("m/qr_move_from.html", {"request": request})

# 2) pick item from inventory
@app.get("/m/qr/move/select", response_class=HTMLResponse)
def mobile_qr_move_select(request: Request, from_location: str):
    from_location = (from_location or "").strip().replace(" ", "")
    rows = search_inventory(location=from_location, item_code="")
    return templates.TemplateResponse(
        "m/qr_move_select.html",
        {"request": request, "from_location": from_location, "rows": rows},
    )

# 3) scan to location + submit
@app.get("/m/qr/move/to", response_class=HTMLResponse)
def mobile_qr_move_to(
    request: Request,
    from_location: str,
    item_code: str,
    item_name: str,
    lot: str,
    spec: str,
    qty: int,
):
    # 필수값 검증 고정 (QR 이동도 동일 규칙)
    from_location = _req_nonempty("출발 로케이션", from_location)
    item_code = _req_nonempty("품번", item_code)
    item_name = _req_nonempty("품명", item_name)
    lot = _req_nonempty("LOT", lot)
    spec = _req_nonempty("규격", spec)
    if qty <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")
    return templates.TemplateResponse(
        "m/qr_move_to.html",
        {
            "request": request,
            "from_location": from_location,
            "item_code": item_code,
            "item_name": item_name,
            "lot": lot,
            "spec": spec,
            "qty": qty,
        },
    )

# 4) complete move (POST from form)
@app.post("/m/qr/move/complete", response_class=HTMLResponse)
def mobile_qr_move_complete(
    request: Request,
    from_location: str = Form(...),
    to_location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    qty: int = Form(...),
):
    from_location = _req_nonempty("출발 로케이션", from_location)
    to_location = _req_nonempty("도착 로케이션", to_location)
    item_code = _req_nonempty("품번", item_code)
    item_name = _req_nonempty("품명", item_name)
    lot = _req_nonempty("LOT", lot)
    spec = _req_nonempty("규격", spec)
    if qty <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")

    # QR 이동도 재고 필수 필드 동일 고정
    add_move(from_location, to_location, item_code, item_name, lot, spec, "", qty, "QR 이동")
    return templates.TemplateResponse("m/qr_move_done.html", {"request": request})

# QR inventory view helper (optional)
@app.get("/m/qr/inventory", response_class=HTMLResponse)
def mobile_qr_inventory(request: Request, location: str):
    location = (location or "").strip().replace(" ", "")
    rows = search_inventory(location=location, item_code="")
    return templates.TemplateResponse("m/qr_inventory.html", {"request": request, "location": location, "rows": rows})
