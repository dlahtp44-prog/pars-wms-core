
from fastapi import APIRouter
from datetime import datetime
from app.db import get_db, ensure_location_for_write

router = APIRouter(prefix="/api/inbound")

@router.post("")
def inbound(location: str, qty: int):
    ensure_location_for_write(location)
    db = get_db()
    db.execute(
        "INSERT INTO inventory(location_code,qty,updated_at) VALUES(?,?,?)",
        (location, qty, datetime.now().isoformat())
    )
    db.execute(
        "INSERT INTO history(action_type,location_to,qty,created_at) VALUES('INBOUND',?,?,?)",
        (location, qty, datetime.now().isoformat())
    )
    db.commit()
    return {"result":"ok"}
