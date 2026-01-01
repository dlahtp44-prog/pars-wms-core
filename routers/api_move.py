from fastapi import APIRouter, Form, HTTPException
from app.logic import move

router = APIRouter(prefix="/api/move", tags=["move"])

@router.post("")
def move_api(
    from_location: str = Form(...),
    to_location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    qty: int = Form(...),
    brand: str = Form(""),
    note: str = Form(""),
):
    try:
        move(from_location, to_location, item_code, item_name, lot, spec, int(qty), brand, note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True}
