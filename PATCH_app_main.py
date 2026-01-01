
# app/main.py 에 static + router 추가

from fastapi.staticfiles import StaticFiles
from app.pages import mobile_qr

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(mobile_qr.router)
