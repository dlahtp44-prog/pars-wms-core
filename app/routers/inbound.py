
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd
from app.db import get_db

router = APIRouter(prefix="/api/inbound", tags=["inbound"])

def apply_inventory_and_history(cur, location, item_code, item_name, lot, spec, qty, memo):
    # inventory 처리
    cur.execute("""
    SELECT qty FROM inventory
    WHERE location=? AND item_code=? AND lot=? AND spec=?
    """, (location, item_code, lot, spec))
    row = cur.fetchone()

    if row:
        cur.execute("""
        UPDATE inventory
        SET qty = qty + ?
        WHERE location=? AND item_code=? AND lot=? AND spec=?
        """, (qty, location, item_code, lot, spec))
    else:
        cur.execute("""
        INSERT INTO inventory
        (location, item_code, item_name, lot, spec, qty)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (location, item_code, item_name, lot, spec, qty))

    # history 기록
    cur.execute("""
    INSERT INTO history
    (type, location, item_code, item_name, lot, spec, qty, memo)
    VALUES ('입고', ?, ?, ?, ?, ?, ?, ?)
    """, (location, item_code, item_name, lot, spec, qty, memo))


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

    cur.execute("""
    INSERT INTO inbound
    (location, item_code, item_name, lot, spec, qty, memo)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        location, item_code, item_name, lot, spec, qty, memo
    ))

    apply_inventory_and_history(cur, location, item_code, item_name, lot, spec, qty, memo)

    conn.commit()
    return {"result": "ok"}


@router.post("/excel")
def inbound_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="xlsx 파일만 업로드 가능합니다.")

    df = pd.read_excel(file.file)

    required = ["로케이션","품번","품명","LOT","규격","수량"]
    for col in required:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"{col} 컬럼 누락")

    conn = get_db()
    cur = conn.cursor()

    count = 0
    for _, row in df.iterrows():
        location = row["로케이션"]
        item_code = row["품번"]
        item_name = row["품명"]
        lot = row["LOT"]
        spec = row["규격"]
        qty = int(row["수량"])
        memo = row.get("비고","")

        cur.execute("""
        INSERT INTO inbound
        (location, item_code, item_name, lot, spec, qty, memo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            location, item_code, item_name, lot, spec, qty, memo
        ))

        apply_inventory_and_history(cur, location, item_code, item_name, lot, spec, qty, memo)
        count += 1

    conn.commit()
    return {"result": "ok", "inserted": count}
