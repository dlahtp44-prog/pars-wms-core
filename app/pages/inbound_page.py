from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from excel_inbound import process_inbound_excel

router = APIRouter(prefix="/page/inbound", tags=["PAGE-Inbound"])

@router.get("", response_class=HTMLResponse)
def inbound_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "inbound.html", {"request": request}
    )

@router.post("/excel")
async def inbound_excel_upload(file: UploadFile = File(...)):
    process_inbound_excel(file)
    return RedirectResponse("/page/inbound", status_code=303)
