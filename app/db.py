
import sqlite3

def get_db():
    return sqlite3.connect("wms.db", check_same_thread=False)

def init_db():
    db = get_db()
    cur = db.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS inbound (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        warehouse TEXT,
        location TEXT,
        item_code TEXT,
        item_name TEXT,
        qty INTEGER,
        memo TEXT
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS calendar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        memo TEXT
    )
    ''')
    db.commit()
    db.close()
