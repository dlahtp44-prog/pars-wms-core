import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))

DB_PATH = Path(__file__).resolve().parent / "WMS.db"

def now_ts() -> str:
    return datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M:%S")

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Create missing tables/columns needed by v1.5. Existing tables are preserved."""
    with get_db() as conn:
        cur = conn.cursor()

        # 기존 테이블(inbound/outbound/moves/history/calendar_memo)은 유지.
        # v1.5 운영을 위해 inventory/location_master/users/location_retire_history 추가.
        cur.execute("""CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            item_code TEXT NOT NULL,
            item_name TEXT NOT NULL,
            lot TEXT NOT NULL,
            spec TEXT NOT NULL,
            brand TEXT DEFAULT "",
            qty INTEGER NOT NULL,
            note TEXT DEFAULT "",
            updated_at TEXT NOT NULL
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS location_master(
            location_code TEXT PRIMARY KEY,
            is_active INTEGER DEFAULT 1
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS location_retire_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_code TEXT NOT NULL,
            reason TEXT DEFAULT "",
            retired_by TEXT DEFAULT "",
            retired_at TEXT NOT NULL
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )""")

        # seed admin (admin/admin123)
        row = cur.execute("SELECT COUNT(*) AS c FROM users").fetchone()
        if int(row["c"]) == 0:
            cur.execute(
                "INSERT INTO users(username,password,role,is_active,created_at) VALUES(?,?,?,?,?)",
                ("admin","admin123","admin",1, now_ts())
            )

        conn.commit()

def ensure_location_for_write(code: str) -> None:
    """최초 등장 로케이션 자동 활성 생성. 비활성 로케이션은 조회만 가능(쓰기 금지)."""
    code = (code or "").strip()
    if not code:
        raise ValueError("로케이션이 비어있습니다.")
    with get_db() as conn:
        cur = conn.cursor()
        row = cur.execute("SELECT is_active FROM location_master WHERE location_code=?", (code,)).fetchone()
        if row is None:
            cur.execute("INSERT INTO location_master(location_code,is_active) VALUES(?,1)", (code,))
            conn.commit()
            return
        if int(row["is_active"]) == 0:
            raise ValueError("비활성 로케이션은 조회만 가능합니다.")
