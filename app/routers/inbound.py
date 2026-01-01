
from fastapi import APIRouter, HTTPException
from app.db import get_db, ensure_location_active

router = APIRouter(prefix="/api/inbound")

@router.post("")
def inbound(location: str, qty: int):
    ensure_location_active(location)
    db = get_db()
    db.execute("insert into inventory(location,qty) values(?,?)", (location, qty))
    db.commit()
    return {"result":"ok"}
