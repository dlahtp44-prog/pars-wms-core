import os
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def admin_required(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """HTTP Basic admin gate for Excel uploads.
    Set env vars ADMIN_USER / ADMIN_PASS. Defaults: admin / admin.
    """
    admin_user = os.getenv("ADMIN_USER", "admin")
    admin_pass = os.getenv("ADMIN_PASS", "admin")

    user_ok = secrets.compare_digest(credentials.username or "", admin_user)
    pass_ok = secrets.compare_digest(credentials.password or "", admin_pass)
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="관리자 인증이 필요합니다.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
