# === PATCH: page_history (alias fix) ===
@app.get("/page/history", response_class=HTMLResponse)
def page_history(request: Request, limit: int = 200):
    db = get_db()
    rows = db.execute("""
        SELECT
          ts    AS ts,
          type  AS type,
          src   AS src,
          dst   AS dst,
          item  AS item,
          lot   AS lot,
          spec  AS spec,
          brand AS brand,
          qty   AS qty,
          memo  AS memo
        FROM history
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    db.close()
    return templates.TemplateResponse("history.html", {"request": request, "rows": rows, "limit": limit})
