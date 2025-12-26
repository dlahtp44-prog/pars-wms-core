
# app/main.py 에 아래 import + include 추가

from app.pages import inbound, outbound, move

app.include_router(inbound.router)
app.include_router(outbound.router)
app.include_router(move.router)
