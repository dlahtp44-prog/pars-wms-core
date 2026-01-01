
from fastapi import APIRouter
from app.db import ensure_location_active

router = APIRouter(prefix="/api/move")

@router.post("")
def move(frm: str, to: str):
    ensure_location_active(frm)
    ensure_location_active(to)
    return {"result":"ok"}
