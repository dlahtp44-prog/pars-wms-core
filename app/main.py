
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd

app = FastAPI(title="PARS WMS STEP C")
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/inbound", response_class=HTMLResponse)
def inbound(request: Request):
    return templates.TemplateResponse("inbound_excel.html", {"request": request})

@app.post("/inbound/upload", response_class=HTMLResponse)
async def inbound_upload(request: Request, file: UploadFile = File(...)):
    df = pd.read_excel(file.file)
    required = ["품번","품명","LOT","규격","수량","로케이션","비고"]
    for col in required:
        if col not in df.columns:
            return HTMLResponse(f"필수 컬럼 누락: {col}", status_code=400)
    rows = df.to_dict(orient="records")
    return templates.TemplateResponse(
        "inbound_preview.html",
        {"request": request, "rows": rows}
    )
