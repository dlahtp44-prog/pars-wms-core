
from fastapi import Depends, HTTPException
from app.db import get_db

def get_current_user():
    db = get_db()
    row = db.execute("SELECT username, role FROM users LIMIT 1").fetchone()
    return {"username": row[0], "role": row[1]}

def admin_required(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한 필요")
