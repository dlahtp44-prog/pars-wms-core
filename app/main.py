
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from urllib.parse import urlencode

from .db import init_db, get_db

app = FastAPI(title="PARS WMS CORE", version="1.0.0")
templates = Jinja2Templates(directory="app/templates")

# session for admin
app.add_middleware(SessionMiddleware, secret_key="pars-wms-secret-2025")

@app.on_event("startup")
def _startup():
    init_db()

def is_admin(request: Request) -> bool:
    return bool(request.session.get("role") == "admin")

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    # 모바일을 기본으로
    return RedirectResponse("/m", status_code=302)

@app.get("/m", response_class=HTMLResponse)
def mobile_menu(request: Request):
    return templates.TemplateResponse("mobile_menu.html", {"request": request, "is_admin": is_admin(request)})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, next: str = "/관리자"):
    return templates.TemplateResponse("login.html", {"request": request, "next": next})

@app.post("/login")
def login(request: Request, password: str = Form(...), next: str = Form("/관리자")):
    import os
    admin_pw = os.getenv("ADMIN_PASSWORD", "admin123")
    if password != admin_pw:
        return templates.TemplateResponse("login.html", {"request": request, "next": next, "error": "비밀번호가 틀렸습니다."}, status_code=401)
    request.session["role"] = "admin"
    return RedirectResponse(next, status_code=303)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/m", status_code=303)

# -------------------------------
# Pages
# -------------------------------
@app.get("/입고", response_class=HTMLResponse)
def inbound_page(request: Request):
    return templates.TemplateResponse("inbound.html", {"request": request})

@app.get("/출고", response_class=HTMLResponse)
def outbound_page(request: Request):
    return templates.TemplateResponse("outbound.html", {"request": request})

@app.get("/이동", response_class=HTMLResponse)
def move_page(request: Request):
    return templates.TemplateResponse("move.html", {"request": request})

@app.get("/m/qr", response_class=HTMLResponse)
def qr_page(request: Request):
    return templates.TemplateResponse("qr.html", {"request": request})

@app.get("/재고", response_class=HTMLResponse)
def inventory_page(request: Request, 창고: str = "", 로케이션: str = "", 품번: str = ""):
    conn = get_db()
    cur = conn.cursor()
    q = "SELECT * FROM 재고 WHERE 1=1"
    params = []
    if 창고:
        q += " AND 창고 = ?"; params.append(창고)
    if 로케이션:
        q += " AND 로케이션 = ?"; params.append(로케이션)
    if 품번:
        q += " AND 품번 = ?"; params.append(품번)
    q += " ORDER BY 로케이션, 품번, LOT"
    rows = cur.execute(q, params).fetchall()
    conn.close()
    return templates.TemplateResponse("inventory.html", {"request": request, "rows": rows, "filters": {"창고": 창고, "로케이션": 로케이션, "품번": 품번}})

@app.get("/이력", response_class=HTMLResponse)
def history_page(request: Request, 구분: str = "", 품번: str = ""):
    conn = get_db()
    cur = conn.cursor()
    q = "SELECT * FROM 이력 WHERE 1=1"
    params=[]
    if 구분:
        q += " AND 구분 = ?"; params.append(구분)
    if 품번:
        q += " AND 품번 = ?"; params.append(품번)
    q += " ORDER BY id DESC LIMIT 300"
    rows = cur.execute(q, params).fetchall()
    conn.close()
    return templates.TemplateResponse("history.html", {"request": request, "rows": rows, "filters": {"구분": 구분, "품번": 품번}})

@app.get("/달력", response_class=HTMLResponse)
def calendar_page(request: Request):
    conn = get_db()
    rows = conn.execute("SELECT * FROM 공용달력 ORDER BY 날짜 DESC, id DESC LIMIT 500").fetchall()
    conn.close()
    return templates.TemplateResponse("calendar.html", {"request": request, "rows": rows, "is_admin": is_admin(request)})

@app.get("/관리자", response_class=HTMLResponse)
def admin_page(request: Request):
    if not is_admin(request):
        return RedirectResponse("/login?next=/관리자", status_code=302)
    return templates.TemplateResponse("admin.html", {"request": request})

# -------------------------------
# APIs
# -------------------------------
@app.post("/api/입고")
def api_inbound(
    창고: str = Form(...),
    로케이션: str = Form(...),
    품번: str = Form(...),
    품명: str = Form(...),
    LOT: str = Form(...),
    규격: str = Form(...),
    수량: int = Form(...),
    비고: str = Form("")
):
    if 수량 <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")
    conn = get_db()
    cur = conn.cursor()
    # normalize
    창고, 로케이션, 품번, 품명, LOT, 규격 = [x.strip() for x in [창고, 로케이션, 품번, 품명, LOT, 규격]]
    비고 = (비고 or "").strip()

    cur.execute("""
    INSERT INTO 재고(창고, 로케이션, 품번, 품명, LOT, 규격, 수량, 비고)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(창고, 로케이션, 품번, LOT)
    DO UPDATE SET
      수량 = 재고.수량 + excluded.수량,
      품명 = excluded.품명,
      규격 = excluded.규격,
      비고 = excluded.비고,
      updated_at = datetime('now','localtime')
    """, (창고, 로케이션, 품번, 품명, LOT, 규격, int(수량), 비고))

    cur.execute("""
    INSERT INTO 이력(구분, 창고, 품번, LOT, 출발로케이션, 도착로케이션, 수량, 비고)
    VALUES ('입고', ?, ?, ?, '', ?, ?, ?)
    """, (창고, 품번, LOT, 로케이션, int(수량), 비고))

    conn.commit()
    conn.close()
    return {"result": "ok"}

@app.post("/api/출고")
def api_outbound(
    창고: str = Form(...),
    로케이션: str = Form(...),
    품번: str = Form(...),
    LOT: str = Form(...),
    수량: int = Form(...),
    비고: str = Form("")
):
    if 수량 <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")
    conn = get_db()
    cur = conn.cursor()
    창고, 로케이션, 품번, LOT = [x.strip() for x in [창고, 로케이션, 품번, LOT]]
    비고 = (비고 or "").strip()

    row = cur.execute("SELECT * FROM 재고 WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?", (창고, 로케이션, 품번, LOT)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="해당 재고가 없습니다.")
    if row["수량"] < 수량:
        conn.close()
        raise HTTPException(status_code=400, detail=f"재고 부족: 현재 {row['수량']}")

    cur.execute("UPDATE 재고 SET 수량=수량-?, updated_at=datetime('now','localtime') WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?",
                (int(수량), 창고, 로케이션, 품번, LOT))
    cur.execute("""
    INSERT INTO 이력(구분, 창고, 품번, LOT, 출발로케이션, 도착로케이션, 수량, 비고)
    VALUES ('출고', ?, ?, ?, ?, '', ?, ?)
    """, (창고, 품번, LOT, 로케이션, int(수량), 비고))
    conn.commit()
    conn.close()
    return {"result": "ok"}

@app.post("/api/이동")
def api_move(
    창고: str = Form(...),
    출발로케이션: str = Form(...),
    도착로케이션: str = Form(...),
    품번: str = Form(...),
    LOT: str = Form(...),
    수량: int = Form(...),
    비고: str = Form("")
):
    if 수량 <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")
    conn = get_db()
    cur = conn.cursor()

    창고 = 창고.strip()
    출발로케이션 = 출발로케이션.strip()
    도착로케이션 = 도착로케이션.strip()
    품번 = 품번.strip()
    LOT = LOT.strip()
    비고 = (비고 or "").strip()

    src = cur.execute("SELECT * FROM 재고 WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?", (창고, 출발로케이션, 품번, LOT)).fetchone()
    if not src:
        conn.close()
        raise HTTPException(status_code=404, detail="출발지 재고가 없습니다.")
    if src["수량"] < 수량:
        conn.close()
        raise HTTPException(status_code=400, detail=f"재고 부족: 현재 {src['수량']}")

    # subtract from source
    cur.execute("UPDATE 재고 SET 수량=수량-?, updated_at=datetime('now','localtime') WHERE 창고=? AND 로케이션=? AND 품번=? AND LOT=?",
                (int(수량), 창고, 출발로케이션, 품번, LOT))

    # upsert to destination (keep 품명/규격 from src)
    cur.execute("""
    INSERT INTO 재고(창고, 로케이션, 품번, 품명, LOT, 규격, 수량, 비고)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(창고, 로케이션, 품번, LOT)
    DO UPDATE SET
      수량 = 재고.수량 + excluded.수량,
      품명 = excluded.품명,
      규격 = excluded.규격,
      비고 = excluded.비고,
      updated_at = datetime('now','localtime')
    """, (창고, 도착로케이션, 품번, src["품명"], LOT, src["규격"], int(수량), 비고))

    cur.execute("""
    INSERT INTO 이력(구분, 창고, 품번, LOT, 출발로케이션, 도착로케이션, 수량, 비고)
    VALUES ('이동', ?, ?, ?, ?, ?, ?, ?)
    """, (창고, 품번, LOT, 출발로케이션, 도착로케이션, int(수량), 비고))

    conn.commit()
    conn.close()
    return {"result": "ok"}

@app.get("/api/재고")
def api_inventory():
    conn = get_db()
    rows = conn.execute("SELECT * FROM 재고 ORDER BY 로케이션, 품번, LOT").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/재고/로케이션")
def api_inventory_location(창고: str, 로케이션: str):
    conn = get_db()
    rows = conn.execute("SELECT * FROM 재고 WHERE 창고=? AND 로케이션=? ORDER BY 품번, LOT", (창고, 로케이션)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/이력")
def api_history():
    conn = get_db()
    rows = conn.execute("SELECT * FROM 이력 ORDER BY id DESC LIMIT 500").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/api/달력/추가")
def api_calendar_add(request: Request, 날짜: str = Form(...), 제목: str = Form(...), 내용: str = Form(...)):
    # anyone can add (as requested), admin can edit/delete
    conn = get_db()
    conn.execute("INSERT INTO 공용달력(날짜, 제목, 내용) VALUES (?,?,?)", (날짜, 제목, 내용))
    conn.commit()
    conn.close()
    return RedirectResponse("/달력", status_code=303)

@app.post("/api/달력/수정")
def api_calendar_edit(request: Request, id: int = Form(...), 날짜: str = Form(...), 제목: str = Form(...), 내용: str = Form(...)):
    if not is_admin(request):
        raise HTTPException(status_code=401, detail="관리자만 수정 가능합니다.")
    conn = get_db()
    conn.execute("UPDATE 공용달력 SET 날짜=?, 제목=?, 내용=?, updated_at=datetime('now','localtime') WHERE id=?", (날짜, 제목, 내용, int(id)))
    conn.commit()
    conn.close()
    return RedirectResponse("/달력", status_code=303)

@app.post("/api/달력/삭제")
def api_calendar_delete(request: Request, id: int = Form(...)):
    if not is_admin(request):
        raise HTTPException(status_code=401, detail="관리자만 삭제 가능합니다.")
    conn = get_db()
    conn.execute("DELETE FROM 공용달력 WHERE id=?", (int(id),))
    conn.commit()
    conn.close()
    return RedirectResponse("/달력", status_code=303)

# Simple ping
@app.get("/health")
def health():
    return {"ok": True}
