from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import date
import os, uuid

from app.db import (
    init_db,
    add_inbound, add_outbound, add_move,
    search_inventory, get_history,
    inventory_to_xlsx, history_to_xlsx,
    parse_inbound_xlsx, parse_outbound_xlsx, parse_move_xlsx,
    get_calendar_memos_for_month
)

# =====================================================
# APP INIT (❗ 반드시 1번만)
# =====================================================
app = FastAPI(title="PARS WMS")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# =====================================================
# STARTUP
# =====================================================
@app.on_event("startup")
def startup():
    init_db()
    app.state.downloads = {}

# =====================================================
# 📱 모바일 QR
# =====================================================
@app.get("/m/qr", response_class=HTMLResponse)
def mobile_qr(request: Request):
    return templates.TemplateResponse("m/qr.html", {"request": request})

@app.post("/m/qr/submit")
def mobile_qr_submit(location: str = Form(...)):
    return RedirectResponse(
        url=f"/m/qr/inventory?location={location}",
        status_code=302
    )

@app.get("/m/qr/inventory", response_class=HTMLResponse)
def mobile_qr_inventory(request: Request, location: str):
    rows = search_inventory(location=location, item_code="")
    return templates.TemplateResponse(
        "mobile/qr_inventory.html",
        {"request": request, "location": location, "rows": rows}
    )

# =====================================================
# 🖥 기본 페이지
# =====================================================
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/page/inventory", response_class=HTMLResponse)
def page_inventory(request: Request, location: str = "", item_code: str = ""):
    rows = search_inventory(location=location, item_code=item_code)
    return templates.TemplateResponse(
        "inventory.html",
        {"request": request, "rows": rows, "location": location, "item_code": item_code}
    )

# =====================================================
# 📥📤 API (입고 / 출고 / 이동)
# =====================================================
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

# =====================================================
# 📤 엑셀 업로드
# =====================================================
@app.post("/page/inbound/excel")
async def inbound_excel(file: UploadFile = File(...)):
    rows = parse_inbound_xlsx(await file.read())
    for r in rows:
        add_inbound(**r)
    return {"count": len(rows)}

@app.post("/page/outbound/excel")
async def outbound_excel(file: UploadFile = File(...)):
    rows = parse_outbound_xlsx(await file.read())
    for r in rows:
        add_outbound(**r)
    return {"count": len(rows)}

@app.post("/page/move/excel")
async def move_excel(file: UploadFile = File(...)):
    rows = parse_move_xlsx(await file.read())
    for r in rows:
        add_move(**r)
    return {"count": len(rows)}

# =====================================================
# 📥 엑셀 다운로드
# =====================================================
@app.get("/page/inventory.xlsx")
def inventory_xlsx(location: str = "", item_code: str = ""):
    xbytes = inventory_to_xlsx(
        search_inventory(location=location, item_code=item_code)
    )
    token = uuid.uuid4().hex
    path = f"/tmp/inventory_{token}.xlsx"
    with open(path, "wb") as f:
        f.write(xbytes)
    return FileResponse(path, filename="inventory.xlsx")

@app.get("/page/history.xlsx")
def history_xlsx(limit: int = 200):
    xbytes = history_to_xlsx(get_history(limit=limit))
    token = uuid.uuid4().hex
    path = f"/tmp/history_{token}.xlsx"
    with open(path, "wb") as f:
        f.write(xbytes)
    return FileResponse(path, filename="history.xlsx")
