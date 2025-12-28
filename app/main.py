
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os

from app.db import init_db

app = FastAPI(title="PARS WMS CORE")

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET","pars-wms-secret")
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def start_page(request: Request):
    return templates.TemplateResponse("mobile_menu.html", {"request": request})
