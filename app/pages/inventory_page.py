
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter(prefix="/page/inventory")

@router.get("", response_class=HTMLResponse)
def page(request: Request):
    return request.app.state.templates.TemplateResponse("inventory.html", {"request": request})

@router.get("/xlsx")
def download():
    path = "static/inventory.xlsx"
    return FileResponse(path, filename="inventory.xlsx")
