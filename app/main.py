from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.db import init_db, get_db

app = FastAPI(title="PARS WMS CORE", version="A-1.0.0")
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def _startup():
    init_db()

# ----------------------
# Home / Menu
# ----------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# ----------------------
# Inbound (UI)
# ----------------------
@app.get("/inbound", response_class=HTMLResponse)
def inbound_page(request: Request):
    return templates.TemplateResponse("inbound.html", {"request": request})

@app.post("/api/inbound")
def inbound_save(
    warehouse: str = Form(...),
    location: str = Form(...),
    product_code: str = Form(...),
    product_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    quantity: int = Form(...),
    memo: str = Form(""),
):
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")

    warehouse = warehouse.strip()
    location = location.strip()
    product_code = product_code.strip()
    product_name = product_name.strip()
    lot = lot.strip()
    spec = spec.strip()
    memo = (memo or "").strip()

    conn = get_db()
    cur = conn.cursor()
    now = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute(
        """
        INSERT INTO inbound(warehouse, location, product_code, product_name, lot, spec, quantity, memo, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (warehouse, location, product_code, product_name, lot, spec, int(quantity), memo, now),
    )
    inbound_id = cur.lastrowid

    cur.execute(
        """
        INSERT INTO history(action, ref_table, ref_id, warehouse, location_from, location_to, product_code, lot, quantity, memo, created_at)
        VALUES ('INBOUND', 'inbound', ?, ?, '', ?, ?, ?, ?, ?, ?)
        """,
        (inbound_id, warehouse, location, product_code, lot, int(quantity), memo, now),
    )

    conn.commit()
    conn.close()

    return RedirectResponse(url=f"/inbound/success/{inbound_id}", status_code=303)

@app.get("/inbound/success/{inbound_id}", response_class=HTMLResponse)
def inbound_success(request: Request, inbound_id: int):
    conn = get_db()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM inbound WHERE id = ?", (inbound_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="입고 데이터가 없습니다.")
    return templates.TemplateResponse("inbound_success.html", {"request": request, "row": row})


@app.get("/outbound", response_class=HTMLResponse)
def outbound_page(request: Request):
    return templates.TemplateResponse("outbound.html", {"request": request})

@app.get("/move", response_class=HTMLResponse)
def move_page(request: Request):
    return templates.TemplateResponse("move.html", {"request": request})

# ----------------------
# Print: Formtec labels
# - LS-3108: 99.1 x 38.1mm, 14-up (2x7)
# - LS-3118: 99.1 x 140mm, 4-up (2x2)
# Product label content: 품번/품명/LOT/규격 (요청 반영)
# ----------------------
def _get_inbound(inbound_id: int):
    conn = get_db()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM inbound WHERE id = ?", (inbound_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="입고 데이터가 없습니다.")
    return row

@app.get("/print/ls-3108/{inbound_id}", response_class=HTMLResponse)
def print_ls3108(request: Request, inbound_id: int, mode: str = "one"):
    row = _get_inbound(inbound_id)
    # mode: one | all
    return templates.TemplateResponse("print_ls3108.html", {"request": request, "row": row, "mode": mode})

@app.get("/print/ls-3118/{inbound_id}", response_class=HTMLResponse)
def print_ls3118(request: Request, inbound_id: int, mode: str = "one"):
    row = _get_inbound(inbound_id)
    return templates.TemplateResponse("print_ls3118.html", {"request": request, "row": row, "mode": mode})

# ----------------------
# Inventory / History (minimal list + print button placeholders for later)
# ----------------------
@app.get("/inventory", response_class=HTMLResponse)
def inventory_page(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})

@app.get("/history", response_class=HTMLResponse)
def history_page(request: Request):
    conn = get_db()
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM history ORDER BY id DESC LIMIT 200").fetchall()
    conn.close()
    return templates.TemplateResponse("history.html", {"request": request, "rows": rows})

# ----------------------
# QR / Calendar / Admin (menu only for now; next steps will implement)
# ----------------------
@app.get("/qr", response_class=HTMLResponse)
def qr_page(request: Request):
    return templates.TemplateResponse("qr.html", {"request": request})

@app.get("/calendar", response_class=HTMLResponse)
def calendar_page(request: Request):
    return templates.TemplateResponse("calendar.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    # show recent inbound rows for printing
    conn = get_db()
    cur = conn.cursor()
    inbound_rows = cur.execute("SELECT * FROM inbound ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return templates.TemplateResponse("admin.html", {"request": request, "inbound_rows": inbound_rows})
