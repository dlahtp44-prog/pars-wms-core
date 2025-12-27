
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="PARS WMS CORE UI")

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("mobile_home.html", {"request": request})

@app.get("/m/calendar", response_class=HTMLResponse)
def calendar(request: Request):
    return templates.TemplateResponse("mobile_calendar.html", {"request": request})

@app.get("/m/qr", response_class=HTMLResponse)
def qr(request: Request):
    return templates.TemplateResponse("mobile_qr.html", {"request": request})
