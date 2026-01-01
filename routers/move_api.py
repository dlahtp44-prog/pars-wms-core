from fastapi import APIRouter, Form, HTTPException
from app.logic import move

router = APIRouter(prefix="/api/move", tags=["move"])

@router.post("")
def move_api(
    src_location: str = Form(...),
    dst_location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    brand: str = Form(""),
    qty: int = Form(...),
    note: str = Form(""),
):
    try:
        move(src_location, dst_location, item_code, item_name, lot, spec, int(qty), brand, note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True}
