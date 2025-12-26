
# app/main.py 에 추가

from app.pages import excel_outbound, excel_move

app.include_router(excel_outbound.router)
app.include_router(excel_move.router)
