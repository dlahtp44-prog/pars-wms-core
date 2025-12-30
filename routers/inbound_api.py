from fastapi import APIRouter, Form, HTTPException
from app.db import get_db, now_ts

router = APIRouter(prefix="/api/inbound", tags=["inbound"])

@router.post("")
def inbound(
    location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    brand: str = Form(""),
    qty: int = Form(...),
    note: str = Form(""),
):
    if qty <= 0:
        raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")
    ts = now_ts()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO inbound(ts,location,item_code,item_name,lot,spec,brand,qty,note) VALUES(?,?,?,?,?,?,?,?,?)",
            (ts, location, item_code, item_name, lot, spec, brand, qty, note),
        )
        cur.execute(
            "INSERT INTO history(ts,kind,location,src_location,item_code,item_name,lot,spec,brand,qty,note) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (ts, "inbound", location, "", item_code, item_name, lot, spec, brand, qty, note),
        )
    return {"ok": True}
