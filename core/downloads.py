from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import secrets
from typing import Dict, Optional, Tuple

KST = timezone(timedelta(hours=9))

@dataclass
class DownloadItem:
    filename: str
    content_type: str
    data: bytes
    expires_at: datetime

_store: Dict[str, DownloadItem] = {}

def create_token(data: bytes, filename: str, content_type: str = "application/octet-stream", ttl_minutes: int = 20) -> str:
    token = secrets.token_urlsafe(24)
    _store[token] = DownloadItem(
        filename=filename,
        content_type=content_type,
        data=data,
        expires_at=datetime.now(tz=KST) + timedelta(minutes=ttl_minutes),
    )
    return token

def pop_token(token: str) -> Optional[DownloadItem]:
    item = _store.get(token)
    if not item:
        return None
    if datetime.now(tz=KST) > item.expires_at:
        _store.pop(token, None)
        return None
    # one-time download
    _store.pop(token, None)
    return item
