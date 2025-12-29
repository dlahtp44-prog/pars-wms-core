from fastapi import Request
from app.db import get_db

def is_admin(request: Request) -> bool:
    return bool(request.session.get("admin") is True)

def try_login(username: str, password: str) -> bool:
    conn = get_db()
    row = conn.execute("SELECT username,password,role FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if not row:
        return False
    return row["password"] == password and row["role"] == "admin"
