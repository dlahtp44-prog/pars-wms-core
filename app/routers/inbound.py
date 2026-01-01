
from fastapi import APIRouter, HTTPException
from app.db import get_db, ensure_location_for_write

router = APIRouter(prefix="/api/inbound")

@router.post("")
def inbound(location: str, qty: int):
    ensure_location_for_write(location)
    db = get_db()
    db.execute(
        "INSERT INTO inventory(location_code,qty) VALUES(?,?)",
        (location, qty)
    )
    db.commit()
    return {"result": "ok"}
