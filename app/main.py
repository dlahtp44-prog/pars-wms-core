
import os
import sqlite3
import io
from typing import Optional

from fastapi import FastAPI, Request, Form, Query, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

APP_TITLE = "PARS WMS CORE"
ADMIN_PIN = os.getenv("ADMIN_PIN", "0000")
DB_PATH = os.getenv("DB_PATH", "wms.db")

app = FastAPI(title=APP_TITLE, version="2.0.0")
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "pars-wms-session-secret"))

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    c = db.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS stock (
        item TEXT NOT NULL,
        item_name TEXT NOT NULL DEFAULT '',
        lot TEXT NOT NULL DEFAULT '',
        spec TEXT NOT NULL DEFAULT '',
        location TEXT NOT NULL,
        qty INTEGER NOT NULL,
        updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        PRIMARY KEY(item, lot, location)
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        item TEXT NOT NULL,
        item_name TEXT NOT NULL DEFAULT '',
        lot TEXT NOT NULL DEFAULT '',
        spec TEXT NOT NULL DEFAULT '',
        qty INTEGER NOT NULL,
        src TEXT NOT NULL DEFAULT '',
        dst TEXT NOT NULL DEFAULT '',
        memo TEXT NOT NULL DEFAULT '',
        ts TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS calendar_memo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        memo TEXT NOT NULL,
        author TEXT NOT NULL DEFAULT '',
        updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    )""")

# --- MIGRATION: add missing columns (brand/memo/updated_at) ---
def _col_exists(table: str, col: str) -> bool:
    cols = [r["name"] for r in c.execute(f"PRAGMA table_info({table})").fetchall()]
    return col in cols

# stock: brand, memo
if not _col_exists("stock", "brand"):
    c.execute("ALTER TABLE stock ADD COLUMN brand TEXT NOT NULL DEFAULT ''")
if not _col_exists("stock", "memo"):
    c.execute("ALTER TABLE stock ADD COLUMN memo TEXT NOT NULL DEFAULT ''")

# history: brand, updated_at
if not _col_exists("history", "brand"):
    c.execute("ALTER TABLE history ADD COLUMN brand TEXT NOT NULL DEFAULT ''")
if not _col_exists("history", "updated_at"):
    c.execute("ALTER TABLE history ADD COLUMN updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))")
    db.commit()
    db.close()

@app.on_event("startup")
def _startup():
    init_db()

# --- Quiet icon routes to avoid noise 404s ---
@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

@app.get("/apple-touch-icon.png")
@app.get("/apple-touch-icon-precomposed.png")
def apple_icons():
    return Response(status_code=204)


@app.get("/api/inventory/excel")
def api_inventory_excel():
    try:
        from openpyxl import Workbook
    except Exception:
        raise HTTPException(status_code=500, detail="openpyxl 필요")
    db = get_db()
    rows = db.execute("SELECT location,item,lot,spec,brand,qty,updated_at,memo FROM stock ORDER BY location,item,lot").fetchall()
    db.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "재고"
    ws.append(["로케이션","품번","LOT","규격","브랜드","수량","업데이트","비고"])
    for r in rows:
        ws.append([r["location"], r["item"], r["lot"], r["spec"], r["brand"], r["qty"], r["updated_at"], r["memo"]])

    bio = io.BytesIO()
    wb.save(bio)
    bio.seek(0)
    return StreamingResponse(
        bio,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition":"attachment; filename=inventory.xlsx"}
    )

@app.get("/api/history/excel")
def api_history_excel():
    try:
        from openpyxl import Workbook
    except Exception:
        raise HTTPException(status_code=500, detail="openpyxl 필요")
    db = get_db()
    rows = db.execute("SELECT type,item,lot,spec,brand,qty,updated_at,memo,src,dst,ts FROM history ORDER BY id DESC").fetchall()
    db.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "이력"
    ws.append(["구분","로케이션","출발","도착","품번","LOT","규격","브랜드","수량","업데이트","비고","시간"])
    for r in rows:
        loc = r["dst"] if r["dst"] else r["src"]
        ws.append([r["type"], loc, r["src"], r["dst"], r["item"], r["lot"], r["spec"], r["brand"], r["qty"], r["updated_at"], r["memo"], r["ts"]])

    bio = io.BytesIO()
    wb.save(bio)
    bio.seek(0)
    return StreamingResponse(
        bio,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition":"attachment; filename=history.xlsx"}
    )


# -----------------------
# Helpers: session QR
# -----------------------
def set_qr(request: Request, key: str, value: str):
    request.session.setdefault("qr", {})
    request.session["qr"][key] = value

def pop_qr(request: Request, key: str) -> str:
    qr = request.session.get("qr", {})
    v = qr.get(key, "")
    if key in qr:
        del qr[key]
        request.session["qr"] = qr
    return v

# -----------------------
# UI: Mobile Menu
# -----------------------
@app.get("/", response_class=HTMLResponse)
def mobile_menu(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request, "title": APP_TITLE})

# Korean alias routes (fixes your logs: /입고 etc.)
@app.get("/입고")
def k_in():
    return RedirectResponse("/page/inbound", status_code=307)

@app.get("/출고")
def k_out():
    return RedirectResponse("/page/outbound", status_code=307)

@app.get("/이동")
def k_move():
    return RedirectResponse("/page/move", status_code=307)

@app.get("/재고")
def k_inv():
    return RedirectResponse("/page/inventory", status_code=307)

@app.get("/이력")
def k_hist():
    return RedirectResponse("/page/history", status_code=307)

@app.get("/달력")
def k_cal():
    return RedirectResponse("/page/calendar", status_code=307)

@app.get("/관리자")
def k_admin():
    return RedirectResponse("/page/admin", status_code=307)

# -----------------------
# UI Pages
# -----------------------
@app.get("/page/inbound", response_class=HTMLResponse)
def page_inbound(request: Request):
    qr_loc = pop_qr(request, "in_loc")
    qr_item = pop_qr(request, "in_item")
    return templates.TemplateResponse("inbound.html", {"request": request, "qr_loc": qr_loc, "qr_item": qr_item})

@app.get("/page/outbound", response_class=HTMLResponse)
def page_outbound(request: Request):
    qr_loc = pop_qr(request, "out_loc")
    qr_item = pop_qr(request, "out_item")
    return templates.TemplateResponse("outbound.html", {"request": request, "qr_loc": qr_loc, "qr_item": qr_item})

@app.get("/page/move", response_class=HTMLResponse)
def page_move(request: Request):
    src = pop_qr(request, "mv_src")
    dst = pop_qr(request, "mv_dst")
    item = pop_qr(request, "mv_item")
    return templates.TemplateResponse("move.html", {"request": request, "src": src, "dst": dst, "item": item})

@app.get("/page/inventory", response_class=HTMLResponse)
def page_inventory(request: Request, location: str = "", item: str = ""):
    db = get_db()
    q = "SELECT item,lot,spec,location,qty,brand,memo,updated_at FROM stock WHERE 1=1"
    args = []
    if location:
        q += " AND location LIKE ?"
        args.append(f"%{location}%")
    if item:
        q += " AND item LIKE ?"
        args.append(f"%{item}%")
    q += " ORDER BY location, item"
    rows = db.execute(q, args).fetchall()
    db.close()
    return templates.TemplateResponse("inventory.html", {"request": request, "rows": rows, "location": location, "item": item})

@app.get("/page/history", response_class=HTMLResponse)
def page_history(request: Request, limit: int = 200):
    db = get_db()
    rows = db.execute("SELECT type,item,lot,spec,qty,brand,memo,updated_at,src,dst,ts FROM history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    db.close()
    return templates.TemplateResponse("history.html", {"request": request, "rows": rows, "limit": limit})

@app.get("/page/calendar", response_class=HTMLResponse)
def page_calendar(request: Request, date: str = ""):
    db = get_db()
    if date:
        rows = db.execute("SELECT id,date,memo,author,updated_at FROM calendar_memo WHERE date=? ORDER BY id DESC", (date,)).fetchall()
    else:
        rows = db.execute("SELECT id,date,memo,author,updated_at FROM calendar_memo ORDER BY date DESC, id DESC LIMIT 200").fetchall()
    db.close()
    return templates.TemplateResponse("calendar.html", {"request": request, "rows": rows, "date": date})

@app.get("/page/admin", response_class=HTMLResponse)
def page_admin(request: Request, pin: str = Query("", alias="pin")):
    authed = request.session.get("admin", False)
    if pin and pin == ADMIN_PIN:
        request.session["admin"] = True
        authed = True
    return templates.TemplateResponse("admin.html", {"request": request, "authed": authed})

# -----------------------
# QR Camera Page
# -----------------------
@app.get("/m/qr", response_class=HTMLResponse)
def page_qr(request: Request, mode: str = "in_loc"):
    # mode: in_loc, in_item, out_loc, out_item, mv_src, mv_dst, mv_item
    return templates.TemplateResponse("qr.html", {"request": request, "mode": mode})

@app.post("/m/qr/save")
def qr_save(request: Request, mode: str = Form(...), value: str = Form(...)):
    value = (value or "").strip()
    if not value:
        return RedirectResponse(f"/m/qr?mode={mode}", status_code=303)
    set_qr(request, mode, value)
    # back mapping
    if mode.startswith("in_"):
        return RedirectResponse("/page/inbound", status_code=303)
    if mode.startswith("out_"):
        return RedirectResponse("/page/outbound", status_code=303)
    if mode.startswith("mv_"):
        return RedirectResponse("/page/move", status_code=303)
    return RedirectResponse("/", status_code=303)

# -----------------------
# APIs (DB real)
# -----------------------

@app.post("/api/inbound")
def api_inbound(
    # ✅ 화면(inbound.html)에서 넘어오는 필드명(item_code)을 지원하기 위해
    # item 과 item_code 둘 다 허용합니다.
    item: str | None = Form(None),
    item_code: str | None = Form(None),
    item_name: str = Form(""),
    lot: str = Form(""),
    spec: str = Form(""),
    brand: str = Form(\"\"),
    location: str = Form(...),
    qty: int = Form(...),
    memo: str = Form(""),
):
    # item 결정 (둘 중 하나는 필수)
    _item = (item or item_code or "").strip()
    if not _item:
        raise HTTPException(status_code=422, detail="품번(item_code)이 필요합니다.")
    location = location.strip()

    db = get_db()

    
# stock upsert (재고)
db.execute(
    """
    INSERT INTO stock(item,item_name,lot,spec,location,qty,brand,memo)
    VALUES(?,?,?,?,?,?,?,?)
    ON CONFLICT(item,lot,location) DO UPDATE SET
      qty = qty + excluded.qty,
      item_name = excluded.item_name,
      spec = excluded.spec,
      brand = CASE WHEN excluded.brand <> '' THEN excluded.brand ELSE stock.brand END,
      memo = CASE WHEN excluded.memo <> '' THEN excluded.memo ELSE stock.memo END,
      updated_at = datetime('now','localtime')
    """,
    (_item, item_name, lot, spec, location, int(qty), brand, memo),
)

    # history (이력)
    db.execute(
        "INSERT INTO history(type,item,item_name,lot,spec,qty,src,dst,memo,brand,updated_at) VALUES('IN',?,?,?,?,?,?,?,?,?,datetime('now','localtime'))",
        (_item, item_name, lot, spec, int(qty), \"\", location, memo, brand),
    )

    db.commit()
    db.close()
    return RedirectResponse("/page/inbound", status_code=303)


@app.post("/api/inbound/excel")
def api_inbound_excel(file: UploadFile = File(...)):
    """
    엑셀 입고 (xlsx)
    필수 컬럼: 로케이션 / 품번 / 품명 / LOT / 규격 / 수량
    선택:I
    비고
    """
    if not (file.filename or "").lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="xlsx 파일만 업로드 가능합니다.")

    try:
        from openpyxl import load_workbook
    except Exception:
        raise HTTPException(status_code=500, detail="openpyxl이 설치되어 있지 않습니다. requirements.txt에 openpyxl 추가 필요")

    wb = load_workbook(file.file, data_only=True)
    ws = wb.active

    # 헤더 읽기
    headers = []
    for cell in ws[1]:
        headers.append(str(cell.value).strip() if cell.value is not None else "")

    # 컬럼 인덱스 맵
    def col_idx(name: str):
        try:
            return headers.index(name)
        except ValueError:
            return None

    required = ["로케이션", "품번", "품명", "LOT", "규격", "수량"]
    for c in required:
        if col_idx(c) is None:
            raise HTTPException(status_code=400, detail=f"엑셀 컬럼 누락: {c}")

    idx_loc = col_idx("로케이션")
    idx_item = col_idx("품번")
    idx_name = col_idx("품명")
    idx_lot = col_idx("LOT")
    idx_spec = col_idx("규격")
    idx_qty = col_idx("수량")
    idx_memo = col_idx("비고")  # optional
    idx_brand = col_idx("브랜드")  # optional

    db = get_db()
    inserted = 0

    # 2행부터 데이터
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row is None:
            continue
        location = str(row[idx_loc]).strip() if row[idx_loc] is not None else ""
        item = str(row[idx_item]).strip() if row[idx_item] is not None else ""
        item_name = str(row[idx_name]).strip() if row[idx_name] is not None else ""
        lot = str(row[idx_lot]).strip() if row[idx_lot] is not None else ""
        spec = str(row[idx_spec]).strip() if row[idx_spec] is not None else ""
        qty_val = row[idx_qty]
        memo = ""
        brand = ""
        if idx_brand is not None and idx_brand < len(row) and row[idx_brand] is not None:
            brand = str(row[idx_brand]).strip()
        if idx_memo is not None and idx_memo < len(row) and row[idx_memo] is not None:
            memo = str(row[idx_memo]).strip()

        # 빈 줄 스킵
        if not (location or item or item_name or lot or spec or qty_val):
            continue

        if not location or not item or qty_val is None:
            raise HTTPException(status_code=400, detail=f"엑셀 필수값 누락 (로케이션/품번/수량): {row}")

        try:
            qty = int(qty_val)
        except Exception:
            raise HTTPException(status_code=400, detail=f"수량은 숫자여야 합니다: {qty_val}")

        # stock upsert
        db.execute(
            """
            INSERT INTO stock(item,item_name,lot,spec,location,qty)
            VALUES(?,?,?,?,?,?)
            ON CONFLICT(item,lot,location) DO UPDATE SET
              qty = qty + excluded.qty,
              item_name = excluded.item_name,
              spec = excluded.spec,
              updated_at = datetime('now','localtime')
            """,
            (item, item_name, lot, spec, location, qty, brand, memo),
        )

        # history
        db.execute(
            "INSERT INTO history(type,item,item_name,lot,spec,qty,src,dst,memo,brand,updated_at) VALUES('IN',?,?,?,?,?,?,?,?,?,datetime('now','localtime'))",
            (item, item_name, lot, spec, qty, \"\", location, memo, brand),
        )

        inserted += 1

    db.commit()
    db.close()
    return RedirectResponse("/page/inbound", status_code=303)

@app.post("/api/outbound")
def api_outbound(
    item: str = Form(...),
    item_name: str = Form(""),
    lot: str = Form(""),
    spec: str = Form(""),
    brand: str = Form(\"\"),
    location: str = Form(...),
    qty: int = Form(...),
    memo: str = Form(""),
):
    item=item.strip(); location=location.strip()
    db=get_db()
    # subtract if exists
    row = db.execute("SELECT qty FROM stock WHERE item=? AND lot=? AND location=?", (item,lot,location)).fetchone()
    cur_qty = int(row["qty"]) if row else 0
    if cur_qty < int(qty):
        db.close()
        return templates.TemplateResponse("message.html", {"request": Request, "title":"출고 오류", "msg":"재고가 부족합니다."}, status_code=400)
    db.execute("UPDATE stock SET qty = qty - ?, updated_at=datetime('now','localtime') WHERE item=? AND lot=? AND location=?",
               (int(qty),item,lot,location))
    db.execute("INSERT INTO history(type,item,item_name,lot,spec,qty,src,dst,memo) VALUES('OUT',?,?,?,?,?,?,?,?)",
               (item,item_name,lot,spec,int(qty),location,"",memo))
    db.commit(); db.close()
    return RedirectResponse("/page/outbound", status_code=303)

@app.post("/api/move")
def api_move(
    item: str = Form(...),
    item_name: str = Form(""),
    lot: str = Form(""),
    spec: str = Form(""),
    src: str = Form(...),
    dst: str = Form(...),
    qty: int = Form(...),
    memo: str = Form(""),
):
    item=item.strip(); src=src.strip(); dst=dst.strip()
    db=get_db()
    row = db.execute("SELECT qty FROM stock WHERE item=? AND lot=? AND location=?", (item,lot,src)).fetchone()
    cur_qty = int(row["qty"]) if row else 0
    if cur_qty < int(qty):
        db.close()
        return JSONResponse({"error":"재고 부족"}, status_code=400)
    # subtract src
    db.execute("UPDATE stock SET qty = qty - ?, updated_at=datetime('now','localtime') WHERE item=? AND lot=? AND location=?",
               (int(qty),item,lot,src))
    # add dst upsert
    db.execute("""
    INSERT INTO stock(item,item_name,lot,spec,location,qty)
    VALUES(?,?,?,?,?,?)
    ON CONFLICT(item,lot,location) DO UPDATE SET
      qty = qty + excluded.qty,
      item_name = excluded.item_name,
      spec = excluded.spec,
      updated_at = datetime('now','localtime')
    """, (item,item_name,lot,spec,dst,int(qty)))
    db.execute("INSERT INTO history(type,item,item_name,lot,spec,qty,src,dst,memo) VALUES('MOVE',?,?,?,?,?,?,?,?)",
               (item,item_name,lot,spec,int(qty),src,dst,memo))
    db.commit(); db.close()
    return RedirectResponse("/page/move", status_code=303)

@app.get("/api/inventory")
def api_inventory(location: Optional[str]=None, item: Optional[str]=None):
    db=get_db()
    q="SELECT item,item_name,lot,spec,location,qty,updated_at FROM stock WHERE 1=1"
    args=[]
    if location:
        q+=" AND location LIKE ?"; args.append(f"%{location}%")
    if item:
        q+=" AND item LIKE ?"; args.append(f"%{item}%")
    q+=" ORDER BY location,item"
    rows=[dict(r) for r in db.execute(q,args).fetchall()]
    db.close()
    return {"rows": rows}

@app.get("/api/history")
def api_history(limit:int=200):
    db=get_db()
    rows=[dict(r) for r in db.execute("SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]
    db.close()
    return {"rows": rows}

@app.post("/api/calendar")
def api_calendar(action: str = Form("add"), id: int = Form(0), date: str = Form(""), memo: str = Form(""), author: str = Form("")):
    db=get_db()
    if action == "add":
        db.execute("INSERT INTO calendar_memo(date,memo,author) VALUES(?,?,?)", (date, memo, author))
    elif action == "update":
        db.execute("UPDATE calendar_memo SET memo=?, author=?, updated_at=datetime('now','localtime') WHERE id=?", (memo, author, id))
    elif action == "delete":
        db.execute("DELETE FROM calendar_memo WHERE id=?", (id,))
    db.commit(); db.close()
    return RedirectResponse("/page/calendar?date="+date, status_code=303)
