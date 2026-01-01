
from fastapi import APIRouter
from app.db import get_db

router = APIRouter(prefix="/admin/location")

@router.get("")
def list_locations():
    db = get_db()
    return db.execute(
        "SELECT location_code,is_active FROM location_master"
    ).fetchall()

@router.post("/toggle")
def toggle(code: str, active: int):
    db = get_db()
    db.execute(
        "UPDATE location_master SET is_active=? WHERE location_code=?",
        (active, code)
    )
    db.commit()
    return {"result": "ok"}
