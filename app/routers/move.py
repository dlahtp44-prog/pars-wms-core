
from fastapi import APIRouter
from datetime import datetime
from app.db import ensure_location_for_write, get_db

router = APIRouter(prefix="/api/move")

@router.post("")
def move(frm: str, to: str, qty: int):
    ensure_location_for_write(frm)
    ensure_location_for_write(to)
    db = get_db()
    db.execute(
        "INSERT INTO history(action_type,location_from,location_to,qty,created_at) VALUES('MOVE',?,?,?,?)",
        (frm, to, qty, datetime.now().isoformat())
    )
    db.commit()
    return {"result":"ok"}
