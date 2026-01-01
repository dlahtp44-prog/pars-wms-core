from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from app.db import get_inventory_excel

router = APIRouter(prefix="/page/inventory", tags=["PAGE-Inventory"])

@router.get("", response_class=HTMLResponse)
def inventory_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "inventory.html", {"request": request}
    )

@router.get(".xlsx")
def inventory_excel(location: str = "", item_code: str = ""):
    file_path = get_inventory_excel(location, item_code)
    return FileResponse(
        file_path,
        filename="inventory.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
