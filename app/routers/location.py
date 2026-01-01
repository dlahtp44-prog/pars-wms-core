
from fastapi import APIRouter
from app.db import get_db

router = APIRouter(prefix="/api/location")

@router.get("/active")
def active_locations():
    db = get_db()
    return db.execute(
        "SELECT location_code FROM location_master WHERE is_active=1"
    ).fetchall()
