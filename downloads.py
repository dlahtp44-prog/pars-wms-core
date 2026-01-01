import os
import time
import secrets
from typing import Dict, Tuple, Optional

_DOWNLOADS: Dict[str, Tuple[str, float]] = {}

def register_file(path: str, ttl_seconds: int = 1800) -> str:
    token = secrets.token_urlsafe(16)
    _DOWNLOADS[token] = (path, time.time() + ttl_seconds)
    return token

def get_path(token: str) -> Optional[str]:
    item = _DOWNLOADS.get(token)
    if not item:
        return None
    path, exp = item
    if time.time() > exp:
        _DOWNLOADS.pop(token, None)
        return None
    if not os.path.exists(path):
        _DOWNLOADS.pop(token, None)
        return None
    return path
