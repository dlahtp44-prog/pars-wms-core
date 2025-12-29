from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from datetime import date

router = APIRouter()

@router.get("/page/calendar")
def calendar_home():
    today = date.today()
    return RedirectResponse(
        f"/page/calendar/month?year={today.year}&month={today.month}"
    )
