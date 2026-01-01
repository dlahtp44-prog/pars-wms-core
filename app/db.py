
import sqlite3

def get_db():
    return sqlite3.connect("wms.db")

def ensure_location_active(code):
    db = get_db()
    row = db.execute("select is_active from location_master where location_code=?", (code,)).fetchone()
    if not row:
        db.execute("insert into location_master(location_code,is_active) values(?,1)", (code,))
        db.commit()
        return
    if row[0] == 0:
        raise Exception("비활성 로케이션")
