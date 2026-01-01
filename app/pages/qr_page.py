from fastapi import APIRouter, Request

router = APIRouter(prefix="/m/qr", tags=["mobile-qr"])

@router.get("")
def qr_home(request: Request):
    return request.app.state.templates.TemplateResponse(
        "mobile/qr_home.html",
        {"request": request}
    )
