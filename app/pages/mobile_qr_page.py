from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/m/qr", tags=["MOBILE-QR"])

@router.get("", response_class=HTMLResponse)
def qr_home(request: Request):
    return request.app.state.templates.TemplateResponse(
        "mobile/qr.html", {"request": request}
    )

@router.get("/move/from", response_class=HTMLResponse)
def qr_move_from(request: Request):
    return request.app.state.templates.TemplateResponse(
        "mobile/qr_move_from.html", {"request": request}
    )
