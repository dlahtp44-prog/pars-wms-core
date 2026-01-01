from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.db import get_db
from app.routers.inbound import inbound

router = APIRouter(prefix="/page/inbound", tags=["page-inbound"])

@router.get("")
def inbound_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "inbound.html",
        {"request": request}
    )

@router.post("")
def inbound_submit(
    request: Request,
    location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    qty: int = Form(...),
    brand: str = Form("")
):
    # 👉 내부 함수 직접 호출 (requests 제거)
    inbound(
        location=location,
        item_code=item_code,
        item_name=item_name,
        lot=lot,
        spec=spec,
        qty=qty,
        brand=brand
    )

    return RedirectResponse(
        url="/page/inbound",
        status_code=303
    )
