
from fastapi import APIRouter, Form, UploadFile, File, HTTPException
import pandas as pd
from app.db import get_db

router = APIRouter(prefix="/api/inbound", tags=["inbound"])

def process(cur, location, item_code, item_name, lot, spec, qty, memo):
    # inbound
    cur.execute("""
    INSERT INTO inbound (location,item_code,item_name,lot,spec,qty,memo)
    VALUES (?,?,?,?,?,?,?)
    """, (location,item_code,item_name,lot,spec,qty,memo))

    # inventory (upsert)
    cur.execute("""
    INSERT INTO inventory (location,item_code,item_name,lot,spec,qty)
    VALUES (?,?,?,?,?,?)
    ON CONFLICT(location,item_code,lot,spec)
    DO UPDATE SET qty = qty + excluded.qty
    """, (location,item_code,item_name,lot,spec,qty))

    # history
    cur.execute("""
    INSERT INTO history (type,location,item_code,item_name,lot,spec,qty,memo)
    VALUES ('입고',?,?,?,?,?,?,?)
    """, (location,item_code,item_name,lot,spec,qty,memo))


# =========================
# 수기 입고 (FORM 전용)
# =========================
@router.post("")
def inbound_manual(
    location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    qty: int = Form(...),
    memo: str = Form("")
):
    conn = get_db()
    cur = conn.cursor()
    process(cur, location, item_code, item_name, lot, spec, qty, memo)
    conn.commit()
    return {"result": "ok"}


# =========================
# 엑셀 입고
# =========================
@router.post("/excel")
def inbound_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="xlsx only")

    df = pd.read_excel(file.file)
    conn = get_db()
    cur = conn.cursor()

    required = ["로케이션","품번","품명","LOT","규격","수량"]
    for c in required:
        if c not in df.columns:
            raise HTTPException(status_code=400, detail=f"{c} 컬럼 누락")

    for _, r in df.iterrows():
        process(
            cur,
            r["로케이션"],
            r["품번"],
            r["품명"],
            r["LOT"],
            r["규격"],
            int(r["수량"]),
            r.get("비고","")
        )

    conn.commit()
    return {"result": "ok", "count": len(df)}
