
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import init_db, get_db

app = FastAPI(title="PARS WMS")

templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request})

@app.get("/입고", response_class=HTMLResponse)
def inbound_page(request: Request):
    return templates.TemplateResponse("inbound.html", {"request": request})

@app.post("/입고")
def inbound_save(
    warehouse: str = Form(...),
    location: str = Form(...),
    item_code: str = Form(...),
    item_name: str = Form(...),
    qty: int = Form(...),
    memo: str = Form("")
):
    db = get_db()
    db.execute(
        "INSERT INTO inbound (warehouse, location, item_code, item_name, qty, memo) VALUES (?,?,?,?,?,?)",
        (warehouse, location, item_code, item_name, qty, memo)
    )
    db.commit()
    db.close()
    return RedirectResponse("/입고", status_code=303)

@app.get("/달력", response_class=HTMLResponse)
def calendar_page(request: Request):
    db = get_db()
    rows = db.execute("SELECT date, memo FROM calendar ORDER BY date").fetchall()
    db.close()
    return templates.TemplateResponse("calendar.html", {"request": request, "rows": rows})

@app.post("/달력")
def calendar_save(date: str = Form(...), memo: str = Form(...)):
    db = get_db()
    db.execute("INSERT INTO calendar (date, memo) VALUES (?,?)", (date, memo))
    db.commit()
    db.close()
    return RedirectResponse("/달력", status_code=303)
