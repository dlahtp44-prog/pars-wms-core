
from fastapi import APIRouter
from datetime import datetime
from app.db import ensure_location_for_write, get_db

router = APIRouter(prefix="/api/outbound")

@router.post("")
def outbound(location: str, qty: int):
    ensure_location_for_write(location)
    db = get_db()
    db.execute(
        "INSERT INTO history(action_type,location_from,qty,created_at) VALUES('OUTBOUND',?,?,?)",
        (location, qty, datetime.now().isoformat())
    )
    db.commit()
    return {"result":"ok"}
