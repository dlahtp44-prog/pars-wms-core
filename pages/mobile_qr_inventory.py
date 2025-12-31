from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db import search_inventory

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/m/qr/inventory", response_class=HTMLResponse)
def mobile_qr_inventory(request: Request, location: str):
    rows = search_inventory(location=location)

    return templates.TemplateResponse(
        "m/qr_inventory.html",
        {
            "request": request,
            "location": location,
            "rows": rows
        }
    )
