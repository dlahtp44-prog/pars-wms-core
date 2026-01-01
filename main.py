
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import date
from typing import Optional
import os, re

from app.db import (
    init_db,
    add_inbound, add_outbound, add_move,
    search_inventory, get_history,
    upsert_calendar_memo, get_calendar_memos_for_month,
    inventory_to_xlsx, history_to_xlsx,
    parse_inbound_xlsx, parse_outbound_xlsx, parse_move_xlsx
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

def _is_mobile(req: Request) -> bool:
    ua = (req.headers.get("user-agent") or "").lower()
    return any(k in ua for k in ["mobile", "android", "iphone", "ipad"])

def _pc_only_guard(req: Request):
    # soft guard: block label/admin on mobile for 실사용 분리
    if _is_mobile(req):
        raise HTTPException(status_code=403, detail="이 페이지는 PC에서만 사용할 수 있습니다.")

# =========================
# PC HOME
# =========================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# =========================
# PC PAGES
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
    return templates.TemplateResponse("inventory.html", {"request": request, "rows": rows, "location": location, "item_code": item_code})

@app.get("/page/history", response_class=HTMLResponse)
def page_history(request: Request, limit: int = 200):
    rows = get_history(limit=limit)
    return templates.TemplateResponse("history.html", {"request": request, "rows": rows, "limit": limit})

@app.get("/page/calendar/month", response_class=HTMLResponse)
def page_calendar_month(request: Request, year: Optional[int] = None, month: Optional[int] = None):
    today = date.today()
    y = year or today.year
    m = month or today.month
    memos = get_calendar_memos_for_month(y, m)
    return templates.TemplateResponse("calendar_month.html", {"request": request, "year": y, "month": m, "memos": memos})

@app.post("/page/calendar/memo")
def page_calendar_memo(
    request: Request,
    memo_date: str = Form(...),
    memo_text: str = Form("")
):
    upsert_calendar_memo(memo_date, memo_text)
    # memo_date: YYYY-MM-DD
    try:
        y, m, _ = memo_date.split("-")
        return RedirectResponse(f"/page/calendar/month?year={int(y)}&month={int(m)}", status_code=303)
    except Exception:
        return RedirectResponse("/page/calendar/month", status_code=303)

# =========================
# API (PC 폼 저장용)  ✅ 로그에 찍히던 /api/* 404 해결
# =========================
@app.post("/api/inbound")
def api_inbound(
    location: str = Form(..., alias="로케이션"),
    item_code: str = Form(..., alias="품번"),
    item_name: str = Form(..., alias="품명"),
    lot: str = Form(..., alias="LOT"),
    spec: str = Form(..., alias="규격"),
    qty: int = Form(..., alias="수량"),
    brand: str = Form("", alias="브랜드"),
    note: str = Form("", alias="비고"),
):
    if qty <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")
    if not (location and item_code and item_name and lot and spec):
        raise HTTPException(status_code=400, detail="필수값(로케이션/품번/품명/LOT/규격) 누락")
    add_inbound(location, item_code, item_name, lot, spec, brand, int(qty), note)
    return RedirectResponse("/page/inbound", status_code=303)

@app.post("/api/outbound")
def api_outbound(
    location: str = Form(..., alias="로케이션"),
    item_code: str = Form(..., alias="품번"),
    item_name: str = Form(..., alias="품명"),
    lot: str = Form(..., alias="LOT"),
    spec: str = Form(..., alias="규격"),
    qty: int = Form(..., alias="수량"),
    brand: str = Form("", alias="브랜드"),
    note: str = Form("", alias="비고"),
):
    if qty <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")
    if not (location and item_code and item_name and lot and spec):
        raise HTTPException(status_code=400, detail="필수값(로케이션/품번/품명/LOT/규격) 누락")
    add_outbound(location, item_code, item_name, lot, spec, brand, int(qty), note)
    return RedirectResponse("/page/outbound", status_code=303)

@app.post("/api/move")
def api_move(
    from_location: str = Form(..., alias="출발로케이션"),
    to_location: str = Form(..., alias="도착로케이션"),
    item_code: str = Form(..., alias="품번"),
    item_name: str = Form(..., alias="품명"),
    lot: str = Form(..., alias="LOT"),
    spec: str = Form(..., alias="규격"),
    qty: int = Form(..., alias="수량"),
    brand: str = Form("", alias="브랜드"),
    note: str = Form("", alias="비고"),
):
    if qty <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")
    if not (from_location and to_location and item_code and item_name and lot and spec):
        raise HTTPException(status_code=400, detail="필수값(출발/도착/품번/품명/LOT/규격) 누락")
    add_move(from_location, to_location, item_code, item_name, lot, spec, brand, int(qty), note)
    return RedirectResponse("/page/move", status_code=303)

# =========================
# EXCEL 업로드 (PC) ✅ /page/*/excel 404 해결
# =========================
@app.post("/page/inbound/excel")
def page_inbound_excel(request: Request, file: UploadFile = File(...)):
    result = parse_inbound_xlsx(file)
    return templates.TemplateResponse("excel_result.html", {"request": request, "title": "입고 엑셀 업로드", "result": result})

@app.post("/page/outbound/excel")
def page_outbound_excel(request: Request, file: UploadFile = File(...)):
    result = parse_outbound_xlsx(file)
    return templates.TemplateResponse("excel_result.html", {"request": request, "title": "출고 엑셀 업로드", "result": result})

@app.post("/page/move/excel")
def page_move_excel(request: Request, file: UploadFile = File(...)):
    result = parse_move_xlsx(file)
    return templates.TemplateResponse("excel_result.html", {"request": request, "title": "이동 엑셀 업로드", "result": result})

# =========================
# EXCEL 다운로드 ✅ /page/*.xlsx 404 해결 (기존 URL 그대로 살림)
# =========================
@app.get("/page/inventory.xlsx")
def download_inventory_xlsx(location: str = "", item_code: str = ""):
    rows = search_inventory(location=location, item_code=item_code)
    data = inventory_to_xlsx(rows)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=inventory.xlsx"},
    )

@app.get("/page/history.xlsx")
def download_history_xlsx(limit: int = 200):
    rows = get_history(limit=limit)
    data = history_to_xlsx(rows)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=history.xlsx"},
    )

# =========================
# ADMIN (PC 전용) - 라벨/관리자 메뉴
# =========================
@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    _pc_only_guard(request)
    return templates.TemplateResponse("admin_menu.html", {"request": request})

@app.get("/admin/labels", response_class=HTMLResponse)
def admin_labels(request: Request):
    _pc_only_guard(request)
    # 기본: 재고 전체
    rows = search_inventory(location="", item_code="")
    return templates.TemplateResponse("admin_labels.html", {"request": request, "rows": rows})

@app.get("/admin/labels/product", response_class=HTMLResponse)
def admin_labels_product(request: Request, location: str = "", item_code: str = "", copies: int = 1):
    _pc_only_guard(request)
    rows = search_inventory(location=location, item_code=item_code)
    return templates.TemplateResponse("label_formtec_product.html", {"request": request, "rows": rows, "copies": max(1, int(copies))})

@app.get("/admin/labels/location", response_class=HTMLResponse)
def admin_labels_location(request: Request, locations: str = ""):
    _pc_only_guard(request)
    # locations: comma or whitespace separated
    locs = [x.strip() for x in re.split(r"[,
\s]+", locations) if x.strip()] if locations else []
    return templates.TemplateResponse("label_formtec_location.html", {"request": request, "locations": locs})

# =========================
# MOBILE HOME (캡처 UI 스타일)
# =========================
@app.get("/m", response_class=HTMLResponse)
def mobile_home(request: Request):
    return templates.TemplateResponse("m_home.html", {"request": request})


@app.get("/m/outbound", response_class=HTMLResponse)
def mobile_outbound(request: Request):
    return templates.TemplateResponse("m_soon.html", {"request": request, "title": "출고", "message": "모바일 출고는 v1.1에서 추가됩니다. (현재는 PC 또는 QR 이동 기능을 사용하세요.)"})

@app.get("/m/move", response_class=HTMLResponse)
def mobile_move(request: Request):
    return RedirectResponse("/m/qr/move", status_code=303)

@app.get("/m/inventory", response_class=HTMLResponse)
def mobile_inventory(request: Request, location: str = "", item_code: str = ""):
    rows = search_inventory(location=location, item_code=item_code)
    return templates.TemplateResponse("m_inventory.html", {"request": request, "rows": rows, "location": location, "item_code": item_code})

@app.get("/m/history", response_class=HTMLResponse)
def mobile_history(request: Request, limit: int = 100):
    rows = get_history(limit=limit)
    return templates.TemplateResponse("m_history.html", {"request": request, "rows": rows, "limit": limit})

@app.get("/m/calendar", response_class=HTMLResponse)
def mobile_calendar(request: Request):
    return RedirectResponse("/page/calendar/month", status_code=303)

# 모바일: 입고 QR 전용 플로우 (수량 포함)
@app.get("/m/inbound", response_class=HTMLResponse)
def mobile_inbound_scan(request: Request):
    return templates.TemplateResponse("m_inbound_scan.html", {"request": request})

@app.get("/m/inbound/form", response_class=HTMLResponse)
def mobile_inbound_form(request: Request, location: str = ""):
    if not location:
        return RedirectResponse("/m/inbound", status_code=303)
    return templates.TemplateResponse("m_inbound_form.html", {"request": request, "location": location})

@app.post("/m/inbound/complete", response_class=HTMLResponse)
def mobile_inbound_complete(
    request: Request,
    location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    qty: int = Form(...),
    brand: str = Form(""),
    note: str = Form(""),
):
    # 필수값 검증 (PC 엑셀/폼과 동일 기준)
    if not (location and item_code and item_name and lot and spec):
        raise HTTPException(status_code=400, detail="필수값(로케이션/품번/품명/LOT/규격) 누락")
    if int(qty) <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")
    add_inbound(location, item_code, item_name, lot, spec, brand, int(qty), note)
    return templates.TemplateResponse("m_inbound_done.html", {"request": request, "location": location})

# 기존 모바일 QR 이동은 유지 (필요 라우트만 살림)
@app.get("/m/qr/move", response_class=HTMLResponse)
def m_qr_move(request: Request):
    return templates.TemplateResponse("m_move_from.html", {"request": request})

@app.get("/m/qr/move/select", response_class=HTMLResponse)
def m_qr_move_select(request: Request, from_location: str = ""):
    rows = search_inventory(location=from_location, item_code="")
    return templates.TemplateResponse("qr_move_select.html", {"request": request, "from_location": from_location, "rows": rows})

@app.get("/m/qr/move/to", response_class=HTMLResponse)
def m_qr_move_to(request: Request, from_location: str = "", item_code: str = "", lot: str = "", spec: str = "", item_name: str = "", brand: str = ""):
    return templates.TemplateResponse("qr_move_to.html", {"request": request, "from_location": from_location, "item_code": item_code, "lot": lot, "spec": spec, "item_name": item_name, "brand": brand})

@app.post("/m/qr/move/complete")
def m_qr_move_complete(
    request: Request,
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
    if not (from_location and to_location and item_code and item_name and lot and spec):
        raise HTTPException(status_code=400, detail="필수값(출발/도착/품번/품명/LOT/규격) 누락")
    if int(qty) <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")
    add_move(from_location, to_location, item_code, item_name, lot, spec, brand, int(qty), note)
    return RedirectResponse("/m", status_code=303)
