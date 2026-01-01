
import sqlite3
from datetime import datetime

def get_db():
    return sqlite3.connect("wms.db")

def init_db():
    db = get_db()
    db.execute("""CREATE TABLE IF NOT EXISTS location_master(
        location_code TEXT PRIMARY KEY,
        is_active INTEGER DEFAULT 1
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS inventory(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_code TEXT,
        qty INTEGER,
        updated_at TEXT
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_type TEXT,
        location_from TEXT,
        location_to TEXT,
        qty INTEGER,
        created_at TEXT
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS location_retire_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_code TEXT,
        reason TEXT,
        retired_by TEXT,
        retired_at TEXT
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )""")
    # seed admin
    row = db.execute("SELECT COUNT(*) FROM users").fetchone()
    if row[0] == 0:
        db.execute(
            "INSERT INTO users(username,password,role) VALUES('admin','admin123','admin')"
        )
    db.commit()

def ensure_location_for_write(code):
    db = get_db()
    row = db.execute(
        "SELECT is_active FROM location_master WHERE location_code=?",
        (code,)
    ).fetchone()
    if not row:
        db.execute(
            "INSERT INTO location_master(location_code,is_active) VALUES(?,1)",
            (code,)
        )
        db.commit()
        return
    if row[0] == 0:
        raise Exception("비활성 로케이션은 조회만 가능합니다.")
        from datetime import datetime, timezone, timedelta

def now_kst_iso():
    """
    현재 시간을 KST 기준 ISO 문자열로 반환
    예: 2026-01-01T12:34:56
    """
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).replace(microsecond=0).isoformat()

