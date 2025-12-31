from fastapi import (
    FastAPI, Request, Form, UploadFile, File, HTTPException
)
from fastapi.responses import (
    HTMLResponse, RedirectResponse, FileResponse
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import date
from typing import Optional
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
# APP INIT
# =========================
app = FastAPI(title="PARS WMS")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

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
# DESKTOP PAGES
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
            "today": date.today().isoformat(),
        },
    )

@app.post("/page/calendar/memo")
def calendar_add_memo(memo_date: str = Form(...), author: str = Form(""), memo: str = Form(...)):
    upsert_calendar_memo(memo_date, author.strip(), memo.strip())
    y, m, _ = memo_date.split("-")
    return RedirectResponse(url=f"/page/calendar/month?year={int(y)}&month={int(m)}", status_code=303)

# =========================
# 📱 MOBILE HOME / QR
# =========================
@app.get("/m", response_class=HTMLResponse)
def mobile_home(request: Request):
    return templates.TemplateResponse("m/home.html", {"request": request})

@app.get("/m/qr", response_class=HTMLResponse)
def mobile_qr(request: Request):
    return templates.TemplateResponse("m/qr.html", {"request": request})

@app.get("/m/qr/inventory", response_class=HTMLResponse)
def mobile_qr_inventory(request: Request, location: str):
    location = location.strip().replace(" ", "")
    rows = search_inventory(location=location, item_code="")
    return templates.TemplateResponse(
        "m/qr_inventory.html",
        {"request": request, "location": location, "rows": rows}
    )

# =========================
# 🚚 MOBILE QR MOVE (1~4 통합)
# =========================

# 1️⃣ 출발 로케이션 QR
@app.get("/m/qr/move", response_class=HTMLResponse)
def mobile_qr_move_from(request: Request):
    return templates.TemplateResponse("m/qr_move_from.html", {"request": request})

# 2️⃣ 출발 로케이션 재고 선택
@app.get("/m/qr/move/select", response_class=HTMLResponse)
def mobile_qr_move_select(request: Request, from_location: str):
    from_location = from_location.strip().replace(" ", "")
    rows = search_inventory(location=from_location, item_code="")
    return templates.TemplateResponse(
        "m/qr_move_select.html",
        {"request": request, "from_location": from_location, "rows": rows}
    )

# 3️⃣ 도착 로케이션 QR (안전 가드 포함)
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
    # 🔒 안전 가드: 정상 플로우 아니면 처음으로
    if not all([from_location, item_code, item_name, lot, spec, qty]):
        return RedirectResponse(url="/m/qr/move", status_code=302)

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
        }
    )

# 4️⃣ 이동 완료 + DB 반영
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
    from_location = from_location.strip().replace(" ", "")
    to_location = to_location.strip().replace(" ", "")

    if qty <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")

    add_move(
        from_location,
        to_location,
        item_code,
        item_name,
        lot,
        spec,
        "",
        qty,
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
