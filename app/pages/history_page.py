from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from app.db import get_history_excel

router = APIRouter(prefix="/page/history", tags=["PAGE-History"])

@router.get("", response_class=HTMLResponse)
def history_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "history.html", {"request": request}
    )

@router.get(".xlsx")
def history_excel(limit: int = 200):
    file_path = get_history_excel(limit)
    return FileResponse(
        file_path,
        filename="history.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
