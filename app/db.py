
import sqlite3

def get_db():
    return sqlite3.connect("wms.db")

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
