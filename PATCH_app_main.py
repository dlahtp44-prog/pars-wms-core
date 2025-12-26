
# app/main.py 에 추가

from app.pages import admin
app.include_router(admin.router)
