
from fastapi import APIRouter, HTTPException
from app.db import get_db

router = APIRouter(prefix="/admin/location", tags=["LocationAdmin"])

@router.get("")
def list_locations():
    db = get_db()
    return db.execute("select location_code,is_active from location_master").fetchall()

@router.post("/toggle")
def toggle_location(code: str, active: int):
    db = get_db()
    db.execute("update location_master set is_active=? where location_code=?", (active, code))
    db.commit()
    return {"result": "ok"}
