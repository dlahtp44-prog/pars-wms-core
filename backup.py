
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
import os, shutil

router = APIRouter(prefix="/backup")

DB_PATH = "app/wms.db"
BACKUP_PATH = "app/wms_backup.db"

@router.get("/download")
def download_db():
    return FileResponse(DB_PATH, filename="wms_backup.db")

@router.post("/restore")
def restore_db(file: UploadFile = File(...)):
    with open(BACKUP_PATH, "wb") as f:
        shutil.copyfileobj(file.file, f)
    os.replace(BACKUP_PATH, DB_PATH)
    return RedirectResponse("/admin", status_code=302)
