
import sqlite3, io
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import qrcode

app = FastAPI(title="PARS WMS CORE")
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key="pars-wms-secret")

def db():
    return sqlite3.connect("wms.db", check_same_thread=False)

@app.on_event("startup")
def init():
    d=db()
    d.execute("CREATE TABLE IF NOT EXISTS inbound(item TEXT, name TEXT, lot TEXT, spec TEXT)")
    d.execute("CREATE TABLE IF NOT EXISTS locations(code TEXT PRIMARY KEY)")
    d.commit(); d.close()

# ✅ START PAGE (모바일 메뉴)
@app.get("/", response_class=HTMLResponse)
def start(request:Request):
    return templates.TemplateResponse("start.html",{"request":request})

# --- Inbound
@app.get("/inbound", response_class=HTMLResponse)
def inbound(request:Request):
    return templates.TemplateResponse("inbound.html",{"request":request})

@app.post("/api/inbound")
def inbound_save(item:str=Form(...), name:str=Form(...), lot:str=Form(...), spec:str=Form(...)):
    d=db(); d.execute("INSERT INTO inbound VALUES(?,?,?,?)",(item,name,lot,spec)); d.commit(); d.close()
    return RedirectResponse("/print/label",303)

# --- Product label print
@app.get("/print/label", response_class=HTMLResponse)
def print_label(request:Request):
    rows=db().execute("SELECT item,name,lot,spec FROM inbound").fetchall()
    return templates.TemplateResponse("print_label.html",{"request":request,"rows":rows})

# --- Location management
@app.get("/locations", response_class=HTMLResponse)
def locations(request:Request):
    rows=db().execute("SELECT code FROM locations").fetchall()
    return templates.TemplateResponse("locations.html",{"request":request,"rows":rows})

@app.post("/locations")
def add_loc(code:str=Form(...)):
    d=db(); d.execute("INSERT OR IGNORE INTO locations VALUES(?)",(code,)); d.commit(); d.close()
    return RedirectResponse("/locations",303)

@app.get("/print/location", response_class=HTMLResponse)
def print_loc(request:Request):
    rows=db().execute("SELECT code FROM locations").fetchall()
    return templates.TemplateResponse("print_location.html",{"request":request,"rows":rows})

@app.get("/qr/{code}")
def qr_img(code:str):
    img=qrcode.make(code)
    buf=io.BytesIO(); img.save(buf,format="PNG"); buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
