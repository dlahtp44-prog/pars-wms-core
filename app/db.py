import sqlite3
from datetime import datetime, timezone, timedelta

DB_PATH = "wms.db"


# ---------------------------
# DB Connection
# ---------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------
# Init DB
# ---------------------------
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS location_master (
            location_code TEXT PRIMARY KEY,
            is_active INTEGER DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_code TEXT,
            item_code TEXT,
            item_name TEXT,
            lot TEXT,
            spec TEXT,
            qty INTEGER,
            brand TEXT,
            updated_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT,
            location_from TEXT,
            location_to TEXT,
            item_code TEXT,
            lot TEXT,
            qty INTEGER,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS location_retire_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_code TEXT,
            reason TEXT,
            retired_by TEXT,
            retired_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT
        )
    """)

    # seed admin
    row = cur.execute("SELECT COUNT(*) FROM users").fetchone()
    if row[0] == 0:
        cur.execute(
            "INSERT INTO users(username,password,role) VALUES (?,?,?)",
            ("admin", "admin123", "admin")
        )

    conn.commit()
    conn.close()


# ---------------------------
# Location validation
# ---------------------------
def ensure_location_for_write(location_code: str):
    conn = get_db()
    cur = conn.cursor()

    row = cur.execute(
        "SELECT is_active FROM location_master WHERE location_code=?",
        (location_code,)
    ).fetchone()

    if row is None:
        cur.execute(
            "INSERT INTO location_master(location_code,is_active) VALUES (?,1)",
            (location_code,)
        )
        conn.commit()
        conn.close()
        return

    if row["is_active"] == 0:
        conn.close()
        raise Exception("비활성 로케이션은 조회만 가능합니다.")

    conn.close()


# ---------------------------
# Time util
# ---------------------------
def now_kst_iso():
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).replace(microsecond=0).isoformat()


# ---------------------------
# Inventory search (QR)
# ---------------------------
def search_inventory(
    location_code: str = "",
    item_code: str = "",
    lot: str = ""
):
    conn = get_db()
    cur = conn.cursor()

    query = """
        SELECT
            location_code,
            item_code,
            item_name,
            lot,
            spec,
            qty,
            brand
        FROM inventory
        WHERE 1=1
    """
    params = []

    if location_code:
        query += " AND location_code = ?"
        params.append(location_code)

    if item_code:
        query += " AND item_code = ?"
        params.append(item_code)

    if lot:
        query += " AND lot = ?"
        params.append(lot)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    return rows
