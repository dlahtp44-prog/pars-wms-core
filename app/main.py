
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="PARS WMS MOBILE")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("mobile_menu.html", {"request": request})

@app.get("/입고", response_class=HTMLResponse)
def inbound(request: Request):
    return templates.TemplateResponse("page_stub.html", {"request": request, "title": "입고"})

@app.get("/출고", response_class=HTMLResponse)
def outbound(request: Request):
    return templates.TemplateResponse("page_stub.html", {"request": request, "title": "출고"})

@app.get("/이동", response_class=HTMLResponse)
def move(request: Request):
    return templates.TemplateResponse("page_stub.html", {"request": request, "title": "이동"})

@app.get("/m/qr", response_class=HTMLResponse)
def qr(request: Request):
    return templates.TemplateResponse("page_stub.html", {"request": request, "title": "QR 스캔"})

@app.get("/재고", response_class=HTMLResponse)
def inventory(request: Request):
    return templates.TemplateResponse("page_stub.html", {"request": request, "title": "재고 조회"})

@app.get("/이력", response_class=HTMLResponse)
def history(request: Request):
    return templates.TemplateResponse("page_stub.html", {"request": request, "title": "이력 조회"})

@app.get("/달력", response_class=HTMLResponse)
def calendar(request: Request):
    return templates.TemplateResponse("page_stub.html", {"request": request, "title": "달력"})

@app.get("/관리자", response_class=HTMLResponse)
def admin(request: Request):
    return templates.TemplateResponse("page_stub.html", {"request": request, "title": "관리자"})
