
from fastapi import Request
from fastapi.responses import RedirectResponse

def require_admin(request: Request):
    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=302)
