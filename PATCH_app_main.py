
# app/main.py 에 추가

from app.pages import qr_move, qr_location

app.include_router(qr_move.router)
app.include_router(qr_location.router)
