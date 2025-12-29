
import os, sqlite3
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(title="PARS WMS CORE")
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET","pars-wms-secret"))

def get_db():
    return sqlite3.connect("wms.db", check_same_thread=False)

@app.on_event("startup")
def startup():
    db=get_db(); c=db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS stock(item TEXT, location TEXT, qty INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS history(type TEXT, item TEXT, qty INTEGER, src TEXT, dst TEXT, ts TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS calendar(date TEXT, memo TEXT)")
    db.commit(); db.close()

@app.get("/", response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("menu.html",{"request":request})

# Pages
@app.get("/page/inbound", response_class=HTMLResponse)
def inbound(request:Request):
    return templates.TemplateResponse("inbound.html",{"request":request})

@app.get("/page/outbound", response_class=HTMLResponse)
def outbound(request:Request):
    return templates.TemplateResponse("outbound.html",{"request":request})

@app.get("/page/move", response_class=HTMLResponse)
def move(request:Request):
    return templates.TemplateResponse("move.html",{"request":request})

@app.get("/page/qr", response_class=HTMLResponse)
def qr(request:Request):
    return templates.TemplateResponse("qr.html",{"request":request})

@app.get("/page/inventory", response_class=HTMLResponse)
def inventory(request:Request):
    db=get_db()
    rows=db.execute("SELECT item,location,qty FROM stock").fetchall()
    db.close()
    return templates.TemplateResponse("inventory.html",{"request":request,"rows":rows})

@app.get("/page/history", response_class=HTMLResponse)
def history(request:Request):
    db=get_db()
    rows=db.execute("SELECT type,item,qty,src,dst,ts FROM history ORDER BY ts DESC").fetchall()
    db.close()
    return templates.TemplateResponse("history.html",{"request":request,"rows":rows})

@app.get("/page/calendar", response_class=HTMLResponse)
def calendar(request:Request):
    db=get_db()
    rows=db.execute("SELECT date,memo FROM calendar").fetchall()
    db.close()
    return templates.TemplateResponse("calendar.html",{"request":request,"rows":rows})

@app.get("/page/admin", response_class=HTMLResponse)
def admin(request:Request):
    return templates.TemplateResponse("admin.html",{"request":request})

# APIs
@app.post("/api/inbound")
def api_in(item:str=Form(...), location:str=Form(...), qty:int=Form(...)):
    db=get_db()
    db.execute("INSERT INTO stock VALUES(?,?,?)",(item,location,qty))
    db.execute("INSERT INTO history VALUES(?,?,?,?,?,datetime('now'))",("IN",item,qty,"",""))
    db.commit(); db.close()
    return RedirectResponse("/page/inbound",303)

@app.post("/api/outbound")
def api_out(item:str=Form(...), location:str=Form(...), qty:int=Form(...)):
    db=get_db()
    db.execute("INSERT INTO history VALUES(?,?,?,?,?,datetime('now'))",("OUT",item,qty,location,""))
    db.commit(); db.close()
    return RedirectResponse("/page/outbound",303)

@app.post("/api/move")
def api_move(item:str=Form(...), src:str=Form(...), dst:str=Form(...), qty:int=Form(...)):
    db=get_db()
    db.execute("INSERT INTO history VALUES(?,?,?,?,?,datetime('now'))",("MOVE",item,qty,src,dst))
    db.commit(); db.close()
    return RedirectResponse("/page/move",303)

@app.post("/api/calendar")
def api_cal(date:str=Form(...), memo:str=Form(...)):
    db=get_db()
    db.execute("INSERT INTO calendar VALUES(?,?)",(date,memo))
    db.commit(); db.close()
    return RedirectResponse("/page/calendar",303)
