from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from app.core.paths import TEMPLATES_DIR
from fastapi.templating import Jinja2Templates
import tempfile, os

from core.excel_import import parse_xlsx  # we will create parse_xlsx wrapper below
from app.logic import outbound


router = APIRouter(prefix="/page/outbound")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("", response_class=HTMLResponse)
def page(request: Request):
    return templates.TemplateResponse("outbound.html", {"request": request})

@router.post("/excel")
async def excel(file: UploadFile = File(...)):
    # save temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        rows = parse_xlsx(tmp_path, mode="outbound")
        for r in rows:
            if "outbound" == "move":
                move(
                    r["src_location"], r["dst_location"],
                    r["item_code"], r["item_name"], r["lot"], r["spec"],
                    int(r["qty"]), r.get("brand",""), r.get("note","")
                )
            elif "outbound" == "inbound":
                inbound(r["location"], r["item_code"], r["item_name"], r["lot"], r["spec"], int(r["qty"]), r.get("brand",""), r.get("note",""))
            else:
                outbound(r["location"], r["item_code"], r["item_name"], r["lot"], r["spec"], int(r["qty"]), r.get("brand",""), r.get("note",""))
    finally:
        try: os.remove(tmp_path)
        except: pass
    return RedirectResponse("/page/outbound", status_code=303)
