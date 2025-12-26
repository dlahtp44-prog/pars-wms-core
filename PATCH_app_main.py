
# app/main.py 에 추가

from app.routers import calendar as calendar_router
from app.pages import calendar as calendar_page

app.include_router(calendar_router.router)
app.include_router(calendar_page.router)
