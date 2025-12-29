from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from app.db import init_db

# API routers (현재 운영중인 경로: /api/inbound, /api/outbound, /api/move, /api/inventory, /api/history)
from app.routers import inbound, outbound, move, inventory, history

app = FastAPI(title="PARS WMS")

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- DB ----------
@app.on_event("startup")
def _startup():
    init_db()

# ---------- Templates / Static ----------
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ---------- Pages (표준 URL: /page/...) ----------
@app.get("/", include_in_schema=False)
def root():
    # 루트는 모바일 홈으로 보내거나(원하면 /m),
    # 바로 입고등록으로 보내도 됨. (현재는 모바일 홈으로)
    return RedirectResponse(url="/m", status_code=307)

@app.get("/m", response_class=HTMLResponse, include_in_schema=False)
def mobile_home(request: Request):
    return templates.TemplateResponse("mobile_home.html", {"request": request})

@app.get("/page/inbound", response_class=HTMLResponse, include_in_schema=False)
def page_inbound(request: Request):
    return templates.TemplateResponse("inbound.html", {"request": request})

@app.get("/page/inventory", response_class=HTMLResponse, include_in_schema=False)
def page_inventory(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})

@app.get("/page/history", response_class=HTMLResponse, include_in_schema=False)
def page_history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

# ---------- 한글 메뉴 URL (호환용: /입고, /재고, /이력 ...) ----------
@app.get("/입고", include_in_schema=False)
def go_inbound():
    return RedirectResponse(url="/page/inbound", status_code=307)

@app.get("/재고", include_in_schema=False)
def go_inventory():
    return RedirectResponse(url="/page/inventory", status_code=307)

@app.get("/이력", include_in_schema=False)
def go_history():
    return RedirectResponse(url="/page/history", status_code=307)

# ---------- 영문 메뉴 URL (호환용: /inbound, /inventory, /history ...) ----------
@app.get("/inbound", include_in_schema=False)
def go_inbound_en():
    return RedirectResponse(url="/page/inbound", status_code=307)

@app.get("/inventory", include_in_schema=False)
def go_inventory_en():
    return RedirectResponse(url="/page/inventory", status_code=307)

@app.get("/history", include_in_schema=False)
def go_history_en():
    return RedirectResponse(url="/page/history", status_code=307)

# ---------- APIs ----------
app.include_router(inbound.router)
app.include_router(outbound.router)
app.include_router(move.router)
app.include_router(inventory.router)
app.include_router(history.router)
