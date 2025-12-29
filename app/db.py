
import sqlite3

def get_db():
    conn = sqlite3.connect("wms.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS inbound (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_code TEXT,
        item_name TEXT,
        lot TEXT,
        spec TEXT,
        qty INTEGER
    )
    """)
    conn.commit()
    conn.close()
