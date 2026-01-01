
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter(prefix="/page/history")

@router.get("", response_class=HTMLResponse)
def page(request: Request):
    return request.app.state.templates.TemplateResponse("history.html", {"request": request})

@router.get("/xlsx")
def download():
    path = "static/history.xlsx"
    return FileResponse(path, filename="history.xlsx")
