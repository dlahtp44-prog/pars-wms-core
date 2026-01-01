from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.routers.move import move

router = APIRouter(prefix="/page/move", tags=["page-move"])

@router.get("")
def move_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "move.html",
        {"request": request}
    )

@router.post("")
def move_submit(
    request: Request,
    from_location: str = Form(...),
    to_location: str = Form(...),
    item_code: str = Form(...),
    lot: str = Form(...),
    qty: int = Form(...)
):
    move(
        frm=from_location,
        to=to_location,
        item_code=item_code,
        lot=lot,
        qty=qty
    )

    return RedirectResponse(
        url="/page/move",
        status_code=303
    )
