from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from excel_move import process_move_excel

router = APIRouter(prefix="/page/move", tags=["PAGE-Move"])

@router.get("", response_class=HTMLResponse)
def move_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "move.html", {"request": request}
    )

@router.post("/excel")
async def move_excel_upload(file: UploadFile = File(...)):
    process_move_excel(file)
    return RedirectResponse("/page/move", status_code=303)
