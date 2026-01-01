from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get("/입고")
def _in():
    return RedirectResponse("/page/inbound", status_code=307)

@router.get("/출고")
def _out():
    return RedirectResponse("/page/outbound", status_code=307)

@router.get("/이동")
def _mv():
    return RedirectResponse("/page/move", status_code=307)

@router.get("/재고")
def _inv():
    return RedirectResponse("/page/inventory", status_code=307)

@router.get("/이력")
def _hist():
    return RedirectResponse("/page/history", status_code=307)

@router.get("/달력")
def _cal():
    return RedirectResponse("/page/calendar/month", status_code=307)

@router.get("/관리자")
def _adm():
    return RedirectResponse("/page/admin", status_code=307)
