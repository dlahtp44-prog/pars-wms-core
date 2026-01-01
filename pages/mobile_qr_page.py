
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/m/qr")

@router.get("/move/from", response_class=HTMLResponse)
def move_from(request: Request):
    return "<h1>QR 이동 FROM</h1>"

@router.get("/move/to", response_class=HTMLResponse)
def move_to(request: Request):
    return "<h1>QR 이동 TO</h1>"
