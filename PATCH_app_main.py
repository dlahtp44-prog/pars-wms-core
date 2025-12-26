
# app/main.py 에 추가

from app.routers import backup as backup_router
from app.pages import backup as backup_page

app.include_router(backup_router.router)
app.include_router(backup_page.router)
