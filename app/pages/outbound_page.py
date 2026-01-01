from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.routers.outbound import outbound

router = APIRouter(prefix="/page/outbound", tags=["page-outbound"])

@router.get("")
def outbound_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "outbound.html",
        {"request": request}
    )

@router.post("")
def outbound_submit(
    request: Request,
    location: str = Form(...),
    item_code: str = Form(...),
    lot: str = Form(...),
    qty: int = Form(...)
):
    outbound(
        location=location,
        item_code=item_code,
        lot=lot,
        qty=qty
    )

    return RedirectResponse(
        url="/page/outbound",
        status_code=303
    )
