
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd
from app.db import get_db

router = APIRouter(prefix="/api/inbound", tags=["inbound"])

def apply_inventory_and_history(cur, location, item_code, item_name, lot, spec, qty, memo):
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
    """, (location, item_code, item_name, lot, spec, qty, memo))

    apply_inventory_and_history(cur, location, item_code, item_name, lot, spec, qty, memo)

    conn.commit()
    return {"result": "ok"}
