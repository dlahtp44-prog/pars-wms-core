
from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
import requests

router = APIRouter(prefix="/page/move")

@router.get("", response_class=HTMLResponse)
def page(request: Request):
    return request.app.state.templates.TemplateResponse("move.html", {"request": request})

@router.post("/excel")
async def excel(file: UploadFile = File(...)):
    requests.post("http://localhost:8080/api/move", files={"file": (file.filename, await file.read())})
    return RedirectResponse("/page/move", status_code=303)
