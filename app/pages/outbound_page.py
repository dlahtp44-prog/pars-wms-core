
from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
import requests

router = APIRouter(prefix="/page/outbound")

@router.get("", response_class=HTMLResponse)
def page(request: Request):
    return request.app.state.templates.TemplateResponse("outbound.html", {"request": request})

@router.post("/excel")
async def excel(file: UploadFile = File(...)):
    requests.post("http://localhost:8080/api/outbound", files={"file": (file.filename, await file.read())})
    return RedirectResponse("/page/outbound", status_code=303)
