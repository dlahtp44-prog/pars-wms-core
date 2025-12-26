
# app/main.py 에 추가

from starlette.middleware.sessions import SessionMiddleware
from app.routers import auth
from app.pages import login

app.add_middleware(SessionMiddleware, secret_key="pars-wms-secret")

app.include_router(auth.router)
app.include_router(login.router)
