from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from excel_outbound import process_outbound_excel

router = APIRouter(prefix="/page/outbound", tags=["PAGE-Outbound"])

@router.get("", response_class=HTMLResponse)
def outbound_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "outbound.html", {"request": request}
    )

@router.post("/excel")
async def outbound_excel_upload(file: UploadFile = File(...)):
    process_outbound_excel(file)
    return RedirectResponse("/page/outbound", status_code=303)
