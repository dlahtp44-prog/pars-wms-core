
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.db import init_db, get_db

app = FastAPI(title="PARS WMS")
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/inbound", response_class=HTMLResponse)
def inbound(request: Request):
    return templates.TemplateResponse("inbound.html", {"request": request})

@app.post("/inbound/save")
def inbound_save(
    item_code: str = Form(...),
    item_name: str = Form(...),
    lot: str = Form(...),
    spec: str = Form(...),
    qty: int = Form(...)
):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO inbound(item_code,item_name,lot,spec,qty) VALUES (?,?,?,?,?)",
        (item_code, item_name, lot, spec, qty)
    )
    conn.commit()
    conn.close()
    return RedirectResponse("/inbound/complete", status_code=302)

@app.get("/inbound/complete", response_class=HTMLResponse)
def inbound_complete(request: Request):
    return templates.TemplateResponse("inbound_complete.html", {"request": request})
