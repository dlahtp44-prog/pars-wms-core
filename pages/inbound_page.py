
from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
import requests

router = APIRouter(prefix="/page/inbound")

@router.get("", response_class=HTMLResponse)
def page(request: Request):
    return request.app.state.templates.TemplateResponse("inbound.html", {"request": request})

@router.post("/excel")
async def excel(file: UploadFile = File(...)):
    requests.post("http://localhost:8080/api/inbound", files={"file": (file.filename, await file.read())})
    return RedirectResponse("/page/inbound", status_code=303)
