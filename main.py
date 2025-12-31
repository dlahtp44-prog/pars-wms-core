from fastapi import (
    FastAPI, Request, Form, HTTPException
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

# DB 로직
from app.db import (
    init_db,
    add_move,
    search_inventory,
    get_calendar_memos_for_month,
    upsert_calendar_memo,
    get_history
)

app = FastAPI(title="PARS WMS")

# 경로 설정
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
# 📦 모바일 QR 이동 로직 (최종 완성)
# ===============================

# 0️⃣ 출발 로케이션 QR 스캔 (시작 페이지) ✅ [중요]
@app.get("/m/qr/move/from", response_class=HTMLResponse)
def mobile_qr_move_from(request: Request):
    return templates.TemplateResponse(
        "m/qr_move_from.html",
        {"request": request}
    )


# 1️⃣ 재고 선택
@app.get("/m/qr/move/select", response_class=HTMLResponse)
def mobile_qr_move_select(
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


# 2️⃣ 도착 로케이션 QR 카메라
@app.get("/m/qr/move/to", response_class=HTMLResponse)
def mobile_qr_move_to(
    request: Request,
    from_location: str,
    item_code: str,
    item_name: str = "",
    lot: str = "",
    spec: str = "",
    qty: int = 0
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
        }
    )


# 3️⃣ 이동 실행 (도착 QR 인식 후)
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
    from_location = from_location.strip().replace(" ", "")
    to_location = to_location.strip().replace(" ", "")

    if not to_location:
        raise HTTPException(status_code=400, detail="도착 로케이션이 없습니다.")

    if qty <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")

    # ✅ 실제 이동 처리
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

    # ✅ 성공 → 완료 화면
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
