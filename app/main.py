from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import io
import qrcode

from app.db import init_db, get_db
from app.auth import is_admin, try_login
from app.utils import parse_qr

app = FastAPI(title="PARS WMS CORE (Mobile Full)", version="1.0.0")
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key="pars-wms-secret-key")

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/qr/img/{payload}")
def qr_image(payload: str):
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home_mobile.html", {"request": request, "admin": is_admin(request)})

# ---------- 입고 ----------
@app.get("/입고", response_class=HTMLResponse)
def inbound_page(request: Request):
    prefill = request.session.get("qr_prefill", {}) or {}
    return templates.TemplateResponse("inbound.html", {"request": request, "prefill": prefill})

@app.post("/api/입고")
def inbound_save(
    창고: str = Form(...),
    로케이션: str = Form(...),
    품번: str = Form(...),
    품명: str = Form(...),
    LOT: str = Form(...),
    규격: str = Form(...),
    수량: int = Form(...),
    비고: str = Form(""),
):
    if int(수량) <= 0:
        return JSONResponse({"detail": "수량은 1 이상이어야 합니다."}, status_code=400)

    wh = 창고.strip()
    loc = 로케이션.strip()
    code = 품번.strip()
    name = 품명.strip()
    lot = LOT.strip()
    spec = 규격.strip()
    remark = (비고 or "").strip()
    qty = int(수량)

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO inventory(warehouse,location,item_code,item_name,lot,spec,qty,remark)
        VALUES(?,?,?,?,?,?,?,?)
        ON CONFLICT(warehouse,location,item_code,lot) DO UPDATE SET
          qty = inventory.qty + excluded.qty,
          item_name = excluded.item_name,
          spec = excluded.spec,
          remark = excluded.remark,
          updated_at = datetime('now','localtime')
        """,
        (wh, loc, code, name, lot, spec, qty, remark),
    )

    cur.execute(
        """
        INSERT INTO history(type,warehouse,item_code,item_name,lot,spec,from_location,to_location,qty,remark)
        VALUES('입고',?,?,?,?,?,'',?,?,?)
        """,
        (wh, code, name, lot, spec, loc, qty, remark),
    )

    conn.commit()
    conn.close()
    return RedirectResponse("/입고", 303)

# ---------- 출고 ----------
@app.get("/출고", response_class=HTMLResponse)
def outbound_page(request: Request):
    prefill = request.session.get("qr_prefill", {}) or {}
    return templates.TemplateResponse("outbound.html", {"request": request, "prefill": prefill})

@app.post("/api/출고")
def outbound_save(
    창고: str = Form(...),
    로케이션: str = Form(...),
    품번: str = Form(...),
    LOT: str = Form(...),
    수량: int = Form(...),
    비고: str = Form(""),
):
    if int(수량) <= 0:
        return JSONResponse({"detail": "수량은 1 이상이어야 합니다."}, status_code=400)

    wh = 창고.strip()
    loc = 로케이션.strip()
    code = 품번.strip()
    lot = LOT.strip()
    qty = int(수량)
    remark = (비고 or "").strip()

    conn = get_db()
    cur = conn.cursor()

    row = conn.execute(
        """SELECT item_name, spec, qty FROM inventory
           WHERE warehouse=? AND location=? AND item_code=? AND lot=?""",
        (wh, loc, code, lot),
    ).fetchone()

    if not row:
        conn.close()
        return JSONResponse({"detail": "재고가 없습니다."}, status_code=404)
    if row["qty"] < qty:
        conn.close()
        return JSONResponse({"detail": "재고 수량이 부족합니다."}, status_code=400)

    cur.execute(
        """UPDATE inventory SET qty=qty-?, updated_at=datetime('now','localtime')
           WHERE warehouse=? AND location=? AND item_code=? AND lot=?""",
        (qty, wh, loc, code, lot),
    )

    cur.execute(
        """INSERT INTO history(type,warehouse,item_code,item_name,lot,spec,from_location,to_location,qty,remark)
           VALUES('출고',?,?,?,?,?,?, '', ?, ?)""",
        (wh, code, row["item_name"], lot, row["spec"], loc, qty, remark),
    )

    conn.commit()
    conn.close()
    return RedirectResponse("/이력", 303)

# ---------- 이동 (4단계) ----------
@app.get("/이동", response_class=HTMLResponse)
def move_page(request: Request):
    st = request.session.get("move_state") or {"stage": 1}
    request.session["move_state"] = st

    items = []
    if st.get("stage") in (2, 3):
        wh = (st.get("warehouse") or "").strip()
        from_loc = (st.get("from_location") or "").strip()
        if wh and from_loc:
            conn = get_db()
            items = conn.execute(
                """SELECT item_code,item_name,lot,spec,qty FROM inventory
                   WHERE warehouse=? AND location=? AND qty>0
                   ORDER BY item_code, lot""",
                (wh, from_loc),
            ).fetchall()
            conn.close()

    return templates.TemplateResponse("move.html", {"request": request, "state": st, "items": items})

@app.post("/이동/출발")
def move_from(request: Request, 창고: str = Form(...), 출발QR: str = Form(...)):
    parsed = parse_qr(출발QR)
    request.session["move_state"] = {
        "stage": 2,
        "warehouse": 창고.strip(),
        "from_location": (parsed.get("location") or parsed.get("raw") or "").strip(),
    }
    return RedirectResponse("/이동", 303)

@app.post("/이동/선택")
def move_select(request: Request, 품번: str = Form(...), LOT: str = Form(...), 수량: int = Form(...), 비고: str = Form("")):
    st = request.session.get("move_state") or {"stage": 1}
    if st.get("stage") != 2:
        return RedirectResponse("/이동", 303)

    st["stage"] = 3
    st["item_code"] = 품번.strip()
    st["lot"] = LOT.strip()
    st["qty"] = int(수량)
    st["remark"] = (비고 or "").strip()
    request.session["move_state"] = st
    return RedirectResponse("/이동", 303)

@app.post("/이동/도착")
def move_to(request: Request, 도착QR: str = Form(...)):
    st = request.session.get("move_state") or {"stage": 1}
    if st.get("stage") != 3:
        return RedirectResponse("/이동", 303)

    parsed = parse_qr(도착QR)
    to_loc = (parsed.get("location") or parsed.get("raw") or "").strip()

    wh = (st.get("warehouse") or "").strip()
    from_loc = (st.get("from_location") or "").strip()
    code = (st.get("item_code") or "").strip()
    lot = (st.get("lot") or "").strip()
    qty = int(st.get("qty") or 0)
    remark = st.get("remark") or ""

    if not (wh and from_loc and to_loc and code and lot and qty > 0):
        return JSONResponse({"detail": "이동 정보가 부족합니다."}, status_code=400)

    conn = get_db()
    cur = conn.cursor()

    row = conn.execute(
        """SELECT item_name, spec, qty FROM inventory
           WHERE warehouse=? AND location=? AND item_code=? AND lot=?""",
        (wh, from_loc, code, lot),
    ).fetchone()

    if not row:
        conn.close()
        return JSONResponse({"detail": "출발지 재고가 없습니다."}, status_code=404)
    if row["qty"] < qty:
        conn.close()
        return JSONResponse({"detail": "출발지 재고 수량이 부족합니다."}, status_code=400)

    cur.execute(
        """UPDATE inventory SET qty=qty-?, updated_at=datetime('now','localtime')
           WHERE warehouse=? AND location=? AND item_code=? AND lot=?""",
        (qty, wh, from_loc, code, lot),
    )

    cur.execute(
        """INSERT INTO inventory(warehouse,location,item_code,item_name,lot,spec,qty,remark)
           VALUES(?,?,?,?,?,?,?,?)
           ON CONFLICT(warehouse,location,item_code,lot) DO UPDATE SET
             qty = inventory.qty + excluded.qty,
             item_name = excluded.item_name,
             spec = excluded.spec,
             remark = excluded.remark,
             updated_at = datetime('now','localtime')""",
        (wh, to_loc, code, row["item_name"], lot, row["spec"], qty, remark),
    )

    cur.execute(
        """INSERT INTO history(type,warehouse,item_code,item_name,lot,spec,from_location,to_location,qty,remark)
           VALUES('이동',?,?,?,?,?,?,?, ?, ?)""",
        (wh, code, row["item_name"], lot, row["spec"], from_loc, to_loc, qty, remark),
    )

    conn.commit()
    conn.close()

    request.session["move_state"] = {
        "stage": 4,
        "warehouse": wh,
        "from_location": from_loc,
        "to_location": to_loc,
        "item_code": code,
        "lot": lot,
        "qty": qty,
    }
    return RedirectResponse("/이동", 303)

@app.post("/이동/리셋")
def move_reset(request: Request):
    request.session.pop("move_state", None)
    return RedirectResponse("/이동", 303)

# ---------- QR ----------
@app.get("/QR", response_class=HTMLResponse)
def qr_page(request: Request):
    return templates.TemplateResponse("qr_scan.html", {"request": request})

@app.post("/QR/적용")
def qr_apply(request: Request, 대상: str = Form(...), QR값: str = Form(...)):
    parsed = parse_qr(QR값)
    pre = {}
    if parsed.get("location"):
        pre["로케이션"] = parsed["location"]
    if parsed.get("item_code"):
        pre["품번"] = parsed["item_code"]
    request.session["qr_prefill"] = pre
    return RedirectResponse(대상, 303)

# ---------- 재고/이력 ----------
@app.get("/재고", response_class=HTMLResponse)
def inventory_page(request: Request, 창고: str = "", 로케이션: str = ""):
    conn = get_db()
    rows = conn.execute(
        """SELECT warehouse,location,item_code,item_name,lot,spec,qty,remark,updated_at FROM inventory
           WHERE (?='' OR warehouse=?) AND (?='' OR location=?)
           ORDER BY warehouse,location,item_code,lot""",
        (창고, 창고, 로케이션, 로케이션),
    ).fetchall()
    conn.close()
    return templates.TemplateResponse("inventory.html", {"request": request, "rows": rows, "warehouse": 창고, "location": 로케이션})

@app.get("/이력", response_class=HTMLResponse)
def history_page(request: Request, 구분: str = ""):
    conn = get_db()
    rows = conn.execute(
        """SELECT type,warehouse,item_code,item_name,lot,spec,from_location,to_location,qty,remark,created_at
           FROM history WHERE (?='' OR type=?)
           ORDER BY id DESC LIMIT 500""",
        (구분, 구분),
    ).fetchall()
    conn.close()
    return templates.TemplateResponse("history.html", {"request": request, "rows": rows, "type": 구분})

# ---------- 달력 ----------
@app.get("/달력", response_class=HTMLResponse)
def calendar_page(request: Request):
    conn = get_db()
    memos = conn.execute(
        "SELECT id,date,content,created_at,updated_at FROM calendar_memo ORDER BY date DESC, id DESC LIMIT 200"
    ).fetchall()
    conn.close()
    return templates.TemplateResponse("calendar.html", {"request": request, "memos": memos})

@app.post("/달력/추가")
def memo_add(date: str = Form(...), content: str = Form(...)):
    conn = get_db()
    conn.execute("INSERT INTO calendar_memo(date,content) VALUES(?,?)", (date.strip(), content.strip()))
    conn.commit()
    conn.close()
    return RedirectResponse("/달력", 303)

@app.post("/달력/수정")
def memo_edit(id: int = Form(...), content: str = Form(...)):
    conn = get_db()
    conn.execute("UPDATE calendar_memo SET content=?, updated_at=datetime('now','localtime') WHERE id=?", (content.strip(), int(id)))
    conn.commit()
    conn.close()
    return RedirectResponse("/달력", 303)

@app.post("/달력/삭제")
def memo_del(id: int = Form(...)):
    conn = get_db()
    conn.execute("DELETE FROM calendar_memo WHERE id=?", (int(id),))
    conn.commit()
    conn.close()
    return RedirectResponse("/달력", 303)

# ---------- 관리자 ----------
@app.get("/관리자", response_class=HTMLResponse)
def admin_home(request: Request):
    if not is_admin(request):
        return RedirectResponse("/관리자/로그인", 303)
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/관리자/로그인", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": ""})

@app.post("/관리자/로그인")
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if try_login(username.strip(), password.strip()):
        request.session["admin"] = True
        return RedirectResponse("/관리자", 303)
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": "로그인 실패"})

@app.post("/관리자/로그아웃")
def admin_logout(request: Request):
    request.session.pop("admin", None)
    return RedirectResponse("/", 303)

@app.get("/관리자/라벨/제품", response_class=HTMLResponse)
def product_label(request: Request, size: str = "3108"):
    if not is_admin(request):
        return RedirectResponse("/관리자/로그인", 303)
    conn = get_db()
    rows = conn.execute(
        """SELECT item_code AS 품번, item_name AS 품명, lot AS LOT, spec AS 규격
           FROM inventory ORDER BY updated_at DESC LIMIT 14"""
    ).fetchall()
    conn.close()
    return templates.TemplateResponse("print_product_label.html", {"request": request, "rows": rows, "size": size})

@app.get("/관리자/로케이션", response_class=HTMLResponse)
def locations_admin(request: Request):
    if not is_admin(request):
        return RedirectResponse("/관리자/로그인", 303)
    conn = get_db()
    rows = conn.execute("SELECT code, created_at FROM locations ORDER BY code").fetchall()
    conn.close()
    return templates.TemplateResponse("admin_locations.html", {"request": request, "rows": rows})

@app.post("/관리자/로케이션/추가")
def locations_add(request: Request, code: str = Form(...)):
    if not is_admin(request):
        return RedirectResponse("/관리자/로그인", 303)
    code = code.strip()
    if code:
        conn = get_db()
        conn.execute("INSERT OR IGNORE INTO locations(code) VALUES(?)", (code,))
        conn.commit()
        conn.close()
    return RedirectResponse("/관리자/로케이션", 303)

@app.get("/관리자/라벨/로케이션", response_class=HTMLResponse)
def location_labels(request: Request):
    if not is_admin(request):
        return RedirectResponse("/관리자/로그인", 303)
    conn = get_db()
    rows = conn.execute("SELECT code FROM locations ORDER BY code").fetchall()
    conn.close()
    return templates.TemplateResponse("print_location_label.html", {"request": request, "rows": rows})
