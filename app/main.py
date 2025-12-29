
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="PARS WMS CORE")
templates = Jinja2Templates(directory="app/templates")

# ✅ static mount (fix 404)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/inbound", response_class=HTMLResponse)
def inbound(request: Request):
    return templates.TemplateResponse("inbound.html", {"request": request})

@app.get("/outbound", response_class=HTMLResponse)
def outbound(request: Request):
    return templates.TemplateResponse("outbound.html", {"request": request})

@app.get("/move", response_class=HTMLResponse)
def move(request: Request):
    return templates.TemplateResponse("move.html", {"request": request})

@app.get("/inventory", response_class=HTMLResponse)
def inventory(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})

@app.get("/history", response_class=HTMLResponse)
def history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/qr", response_class=HTMLResponse)
def qr(request: Request):
    return templates.TemplateResponse("qr.html", {"request": request})

@app.get("/calendar", response_class=HTMLResponse)
def calendar(request: Request):
    return templates.TemplateResponse("calendar.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})
