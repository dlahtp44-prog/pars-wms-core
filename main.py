from fastapi import (
    FastAPI, Request, Form, UploadFile, File, HTTPException
)
from fastapi.responses import (
    HTMLResponse, RedirectResponse, FileResponse
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import date
import os, uuid

# =========================
# DB / LOGIC
# =========================
from app.db import (
    init_db,
    add_inbound, add_outbound, add_move,
    search_inventory, get_history,
    upsert_calendar_memo, get_calendar_memos_for_month,
    inventory_to_xlsx, history_to_xlsx,
    parse_inbound_xlsx, parse_outbound_xlsx, parse_move_xlsx
)

# =========================
# APP INIT (⚠️ 단 1번만)
# =========================
app = FastAPI(title="PARS WMS")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# =========================
# 상태 저장 (다운로드)
# =========================
app.state.downloads = {}

# =========================
# STARTUP
# =========================
@app.on_event("startup")
def startup():
    init_db()

# =========================
# INDEX
# =========================
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

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
def page_inventory(
    request: Request,
    location: str = "",
    item_code: str = ""
):
    rows = search_inventory(location=location, item_code=item_code)
    return templates.TemplateResponse(
        "inventory.html",
        {
            "request": request,
            "rows": rows,
            "location": location,
            "item_code": item_code
        }
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
def calendar_month(
    request: Request,
    year: int = date.today().year,
    month: int = date.today().month
):
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
    upsert_calendar_memo(
        memo_date,
        author.strip(),
        memo.strip()
    )
    y, m, _ = memo_date.split("-")
    return RedirectResponse(
        url=f"/page/calendar/month?year={int(y)}&month={int(m)}",
        status_code=303
    )

# =========================
# 📱 MOBILE (QR 전용)
# - 테플릿 경로를 app/templates/m/* 로 통일
#   (기존 실제 폴더 구조와 일치)
# =========================
@app.get("/m", response_class=HTMLResponse)
def mobile_home(request: Request):
    return templates.TemplateResponse("m/home.html", {"request": request})


@app.get("/m/qr", response_class=HTMLResponse)
def mobile_qr(request: Request):
    return templates.TemplateResponse("m/qr.html", {"request": request})


@app.get("/m/qr/inventory", response_class=HTMLResponse)
def mobile_qr_inventory(request: Request, location: str):
    # ✅ 모든 QR 로케이션 공통 보정
    location = location.strip().replace(" ", "")

    rows = search_inventory(
        location=location,
        item_code=""
    )

    return templates.TemplateResponse(
        "m/qr_inventory.html",
        {"request": request, "location": location, "rows": rows}
    )


# =========================
# 📦 MOBILE QR 이동 (2-step)
# - Step1: 출발 로케이션 스캔
# - Step2: 상품 선택 → 도착 로케이션 스캔 → 이동 처리
# =========================
@app.get("/m/qr/move", response_class=HTMLResponse)
def mobile_qr_move_from(request: Request):
    return templates.TemplateResponse("m/qr_move_from.html", {"request": request})



@app.get("/m/qr/move/from", response_class=HTMLResponse)
def mobile_qr_move_from(request: Request):
    """모바일 QR 이동: 출발 로케이션 스캔 시작 화면"""
    return templates.TemplateResponse(
        "m/qr_move_from.html",
        {"request": request}
    )

@app.get("/m/qr/move/select", response_class=HTMLResponse)
def mobile_qr_move_select(request: Request, from_location: str):
    from_location = from_location.strip().replace(" ", "")
    rows = search_inventory(location=from_location, item_code="")
    return templates.TemplateResponse(
        "m/qr_move_select.html",
        {"request": request, "from_location": from_location, "rows": rows},
    )


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


@app.post("/m/qr/move/complete", response_class=HTMLResponse)
def mobile_qr_move_complete(
    request: Request,
    from_location: str = Form(...),
    to_location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(""),
    lot: str = Form(""),
    spec: str = Form(""),
    qty: int = Form(...),
):
    """도착 로케이션 QR 인식 후 이동 처리"""
    from_location = (from_location or "").strip().replace(" ", "")
    to_location = (to_location or "").strip().replace(" ", "")

    if not to_location:
        raise HTTPException(status_code=400, detail="도착 로케이션이 없습니다.")
    if qty <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")

    add_move(
        from_location,
        to_location,
        item_code,
        item_name,
        lot,
        spec,
        "",          # brand (없으면 빈값)
        int(qty),
        "QR 이동"
    )

    return templates.TemplateResponse(
        "m/qr_move_done.html",
        {
            "request": request,
            "from_location": from_location,
            "to_location": to_location,
            "item_code": item_code,
            "item_name": item_name,
            "lot": lot,
            "spec": spec,
            "qty": qty,
        }
    )


@app.get("/m/qr/labels", response_class=HTMLResponse)
def mobile_qr_labels(request: Request, location: str = "", kind: str = "product"):
    location = location.strip().replace(" ", "")
    rows = search_inventory(location=location, item_code="") if location else []
    return templates.TemplateResponse(
        "m/qr_labels.html",
        {"request": request, "location": location, "rows": rows, "kind": kind},
    )

# =========================
# API (수기 저장)
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
    add_move(
        from_location, to_location,
        item_code, item_name,
        lot, spec, brand, qty, note
    )
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
    return FileResponse(
        path,
        filename=os.path.basename(path)
    )

# =========================
# EXCEL UPLOAD
# =========================
@app.post("/page/inbound/excel", response_class=HTMLResponse)
async def inbound_excel(request: Request, file: UploadFile = File(...)):
    report = await parse_inbound_xlsx(file)
    token = (
        _save_download("xlsx", report["error_xlsx_bytes"])
        if report.get("error_xlsx_bytes") else None
    )
    return templates.TemplateResponse(
        "excel_result.html",
        {
            "request": request,
            "title": "입고 엑셀 업로드 결과",
            "report": report,
            "download_token": token,
            "back_url": "/page/inbound"
        }
    )

@app.post("/page/outbound/excel", response_class=HTMLResponse)
async def outbound_excel(request: Request, file: UploadFile = File(...)):
    report = await parse_outbound_xlsx(file)
    token = (
        _save_download("xlsx", report["error_xlsx_bytes"])
        if report.get("error_xlsx_bytes") else None
    )
    return templates.TemplateResponse(
        "excel_result.html",
        {
            "request": request,
            "title": "출고 엑셀 업로드 결과",
            "report": report,
            "download_token": token,
            "back_url": "/page/outbound"
        }
    )

@app.post("/page/move/excel", response_class=HTMLResponse)
async def move_excel(request: Request, file: UploadFile = File(...)):
    report = await parse_move_xlsx(file)
    token = (
        _save_download("xlsx", report["error_xlsx_bytes"])
        if report.get("error_xlsx_bytes") else None
    )
    return templates.TemplateResponse(
        "excel_result.html",
        {
            "request": request,
            "title": "이동 엑셀 업로드 결과",
            "report": report,
            "download_token": token,
            "back_url": "/page/move"
        }
    )

# =========================
# EXCEL DOWNLOAD
# =========================
@app.get("/page/inventory.xlsx")
def inventory_xlsx(location: str = "", item_code: str = ""):
    token = _save_download(
        "xlsx",
        inventory_to_xlsx(search_inventory(location, item_code))
    )
    return RedirectResponse(
        url=f"/download/{token}",
        status_code=302
    )

@app.get("/page/history.xlsx")
def history_xlsx(limit: int = 200):
    token = _save_download(
        "xlsx",
        history_to_xlsx(get_history(limit))
    )
    return RedirectResponse(
        url=f"/download/{token}",
        status_code=302
    )
