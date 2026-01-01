from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from datetime import datetime
from zoneinfo import ZoneInfo

router = APIRouter(prefix="/page/calendar", tags=["page-calendar"])

@router.get("")
def calendar_home():
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    return RedirectResponse(url=f"/page/calendar/month?year={now.year}&month={now.month}", status_code=302)
