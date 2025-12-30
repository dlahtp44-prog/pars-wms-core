from fastapi import APIRouter, Form, HTTPException
from app.logic import inbound

router = APIRouter(prefix="/api/inbound", tags=["inbound"])

@router.post("")
def inbound_api(
    location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    qty: int = Form(...),
    brand: str = Form(""),
    note: str = Form(""),
):
    try:
        inbound(location, item_code, item_name, lot, spec, int(qty), brand, note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True}
