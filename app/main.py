from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from app.db import (
    init_db,
    add_move,
    search_inventory,
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


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ===============================
# 📦 모바일 QR 이동 (brand 포함 최종)
# ===============================

# 0️⃣ 출발 로케이션 QR
@app.get("/m/qr/move/from", response_class=HTMLResponse)
def qr_move_from(request: Request):
    return templates.TemplateResponse(
        "m/qr_move_from.html",
        {"request": request}
    )


# 1️⃣ 출발지 재고 선택
@app.get("/m/qr/move/select", response_class=HTMLResponse)
def qr_move_select(
    request: Request,
    from_location: str
):
    from_location = from_location.strip().replace(" ", "")
    rows = search_inventory(location=from_location, item_code="")

    return templates.TemplateResponse(
        "m/qr_move_select.html",
        {
            "request": request,
            "from_location": from_location,
            "rows": rows
        }
    )


# 2️⃣ 도착 로케이션 QR 스캔
@app.get("/m/qr/move/to", response_class=HTMLResponse)
def qr_move_to(
    request: Request,
    from_location: str,
    item_code: str,
    item_name: str,
    lot: str,
    spec: str,
    brand: str,
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
            "brand": brand,
            "qty": qty,
        }
    )


# 3️⃣ 이동 처리 (최종)
@app.post("/m/qr/move/complete", response_class=HTMLResponse)
def qr_move_complete(
    request: Request,
    from_location: str = Form(...),
    to_location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    brand: str = Form(...),
    qty: int = Form(...),
):
    if not to_location:
        raise HTTPException(status_code=400, detail="도착 로케이션 누락")

    if qty <= 0:
        raise HTTPException(status_code=400, detail="수량 오류")

    add_move(
        from_location.strip(),
        to_location.strip(),
        item_code,
        item_name,
        lot,
        spec,
        brand,
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
            "brand": brand,
            "qty": qty,
        }
    )
