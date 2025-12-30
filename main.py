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
from io import BytesIO
import qrcode
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(title="PARS WMS")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

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


# ------------------------------
# QR / LABEL (A4) 기능
# ------------------------------
from typing import List, Dict

def _qr_png_bytes(data: str, box_size: int = 6, border: int = 2) -> bytes:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    bio = BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()

def _labels_pdf(items: List[Dict], label_w_mm: float, label_h_mm: float, cols: int) -> bytes:
    page_w, page_h = A4  # points
    label_w = label_w_mm * mm
    label_h = label_h_mm * mm

    rows = int(page_h // label_h)
    if rows < 1:
        rows = 1

    total_w = cols * label_w
    gap_x = (page_w - total_w) / (cols + 1)
    if gap_x < 3 * mm:
        gap_x = 3 * mm

    total_h = rows * label_h
    gap_y = (page_h - total_h) / (rows + 1)
    if gap_y < 3 * mm:
        gap_y = 3 * mm

    out = BytesIO()
    c = canvas.Canvas(out, pagesize=A4)

    for idx, it in enumerate(items):
        if idx > 0 and idx % (cols * rows) == 0:
            c.showPage()

        page_idx = idx % (cols * rows)
        col = page_idx % cols
        row = page_idx // cols

        x = gap_x + col * (label_w + gap_x)
        y = page_h - (gap_y + (row + 1) * label_h + row * gap_y)

        qr_data = it.get("qr_data", "")
        qr_png = _qr_png_bytes(qr_data, box_size=6, border=1)
        qr_img = ImageReader(BytesIO(qr_png))

        qr_size = min(label_h - 12, label_w * 0.45)
        c.drawImage(qr_img, x + 6, y + label_h - qr_size - 6, qr_size, qr_size, mask="auto")

        tx = x + qr_size + 12
        ty = y + label_h - 12

        c.setFont("Helvetica-Bold", 9)
        c.drawString(tx, ty, str(it.get("title", ""))[:40])

        c.setFont("Helvetica", 8)
        for ln in it.get("lines", []):
            ty -= 12
            if ty < y + 10:
                break
            c.drawString(tx, ty, str(ln)[:60])

    c.save()
    return out.getvalue()

@app.get("/m/qr")
def mobile_qr_menu(request: Request):
    return templates.TemplateResponse("qr_scan.html", {"request": request})

@app.get("/page/qr/location/scan")
def qr_location_scan(request: Request):
    return templates.TemplateResponse("qr_location_scan.html", {"request": request})

@app.get("/page/qr/location")
def qr_location(request: Request, location: str):
    rows = search_inventory(location=location, item_code="")
    return templates.TemplateResponse("qr_location.html", {"request": request, "location": location, "rows": rows})

@app.get("/page/qr/move/scan")
def qr_move_scan(request: Request):
    return templates.TemplateResponse("qr_move_scan.html", {"request": request})

@app.get("/page/qr/move")
def qr_move_select(request: Request, from_location: str):
    rows = search_inventory(location=from_location, item_code="")
    return templates.TemplateResponse("qr_move_select.html", {"request": request, "from_location": from_location, "rows": rows})

@app.post("/page/qr/move/commit")
async def qr_move_commit(request: Request):
    form = await request.form()
    from_location = (form.get("from_location") or "").strip()
    to_location = (form.get("to_location") or "").strip()
    picks = form.getlist("pick")

    if not from_location or not to_location:
        raise HTTPException(status_code=400, detail="출발/도착 로케이션이 필요합니다.")
    if not picks:
        raise HTTPException(status_code=400, detail="이동할 상품을 선택하세요.")

    moved = 0
    errors = []
    for p in picks:
        try:
            i = int(p)
            item_code = (form.get(f"item_code_{i}") or "").strip()
            item_name = (form.get(f"item_name_{i}") or "").strip()
            lot = (form.get(f"lot_{i}") or "").strip()
            spec = (form.get(f"spec_{i}") or "").strip()
            qty = int(form.get(f"qty_{i}") or "0")
            if qty <= 0:
                raise ValueError("수량은 1 이상이어야 합니다.")
            add_move(from_location, to_location, item_code, item_name, lot, spec, "", qty, note="QR 이동")
            moved += 1
        except Exception as e:
            errors.append({"row": p, "error": str(e)})

    report = {"success": moved, "failed": len(errors), "errors": errors, "fail_token": None}
    return templates.TemplateResponse("excel_result.html", {"request": request, "report": report})

@app.get("/page/labels/locations")
def labels_locations_page(request: Request):
    return templates.TemplateResponse("label_locations.html", {"request": request})

@app.post("/page/labels/locations")
async def labels_locations_make(request: Request):
    form = await request.form()
    raw = (form.get("locations") or "").strip()
    locs = [l.strip() for l in raw.splitlines() if l.strip()]
    if not locs:
        raise HTTPException(status_code=400, detail="로케이션을 1개 이상 입력하세요.")

    items = [{"qr_data": loc, "title": loc, "lines": []} for loc in locs]
    pdf = _labels_pdf(items, label_w_mm=99.1, label_h_mm=140.0, cols=2)  # LS-3118
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=locations_labels.pdf"},
    )

@app.post("/page/labels/items")
async def labels_items_make(request: Request):
    form = await request.form()
    picks = form.getlist("pick")
    if not picks:
        raise HTTPException(status_code=400, detail="라벨로 출력할 항목을 선택하세요.")

    items = []
    for p in picks:
        i = int(p)
        item_code = (form.get(f"item_code_{i}") or "").strip()
        item_name = (form.get(f"item_name_{i}") or "").strip()
        lot = (form.get(f"lot_{i}") or "").strip()
        spec = (form.get(f"spec_{i}") or "").strip()

        # QR 값: 품번|품명|LOT|규격 (요청사항)
        qr_data = f"{item_code}|{item_name}|{lot}|{spec}"
        items.append({
            "qr_data": qr_data,
            "title": item_code,
            "lines": [
                f"{item_name}",
                f"LOT: {lot}",
                f"규격: {spec}",
            ],
        })

    pdf = _labels_pdf(items, label_w_mm=99.1, label_h_mm=38.1, cols=2)  # LS-3108
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=item_labels.pdf"},
    )