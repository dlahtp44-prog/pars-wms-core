
# app/main.py 에 추가

from app.pages import excel_inbound
app.include_router(excel_inbound.router)
