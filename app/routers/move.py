
from fastapi import APIRouter, HTTPException
from app.db import ensure_location_for_write

router = APIRouter(prefix="/api/move")

@router.post("")
def move(frm: str, to: str):
    ensure_location_for_write(frm)
    ensure_location_for_write(to)
    return {"result": "ok"}
