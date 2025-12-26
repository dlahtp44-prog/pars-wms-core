from fastapi import APIRouter, Request
from ._common import templates

router = APIRouter()

@router.get("/report")
def page(request: Request):
    return templates.TemplateResponse("report.html", {"request": request})
