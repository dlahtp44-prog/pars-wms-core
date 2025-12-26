
# app/main.py 에 추가

from app.pages import mobile, mobile_inbound, mobile_outbound, mobile_move

app.include_router(mobile.router)
app.include_router(mobile_inbound.router)
app.include_router(mobile_outbound.router)
app.include_router(mobile_move.router)
