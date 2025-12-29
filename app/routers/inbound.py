
from fastapi import APIRouter, Form, UploadFile, File, HTTPException
import pandas as pd
from app.db import get_db

router = APIRouter(prefix="/api/inbound", tags=["inbound"])

def apply_all(cur, data):
    location = data["location"]
    item_code = data["item_code"]
    item_name = data["item_name"]
    lot = data["lot"]
    spec = data["spec"]
    qty = int(data["qty"])
    memo = data.get("memo","")

    cur.execute("""INSERT INTO inbound
    (location,item_code,item_name,lot,spec,qty,memo)
    VALUES (?,?,?,?,?,?,?)""", 
    (location,item_code,item_name,lot,spec,qty,memo))

    cur.execute("""
    INSERT INTO history
    (type,location,item_code,item_name,lot,spec,qty,memo)
    VALUES ('입고',?,?,?,?,?,?,?)""", 
    (location,item_code,item_name,lot,spec,qty,memo))

    cur.execute("""
    INSERT INTO inventory
    (location,item_code,item_name,lot,spec,qty)
    VALUES (?,?,?,?,?,?)
    ON CONFLICT(location,item_code,lot,spec)
    DO UPDATE SET qty = qty + excluded.qty
    """, (location,item_code,item_name,lot,spec,qty))


@router.post("")
def inbound_form(
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

    apply_all(cur, locals())
    conn.commit()
    return {"result":"ok"}


@router.post("/excel")
def inbound_excel(file: UploadFile = File(...)):
    df = pd.read_excel(file.file)
    conn = get_db()
    cur = conn.cursor()

    for _, r in df.iterrows():
        apply_all(cur, {
            "location": r["로케이션"],
            "item_code": r["품번"],
            "item_name": r["품명"],
            "lot": r["LOT"],
            "spec": r["규격"],
            "qty": r["수량"],
            "memo": r.get("비고","")
        })

    conn.commit()
    return {"result":"ok","count":len(df)}
