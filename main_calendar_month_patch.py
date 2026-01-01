# page_calendar_month 추가 라우터
@app.get("/page/calendar/month", response_class=HTMLResponse)
def page_calendar_month(request: Request, year: int, month: int):
    import calendar, datetime
    db = get_db()
    cal = calendar.Calendar(6)
    days = []
    today = datetime.date.today()

    for d in cal.itermonthdates(year, month):
        memos = db.execute(
            "SELECT memo FROM calendar_memo WHERE date=? ORDER BY id",
            (d.isoformat(),)
        ).fetchall()
        days.append({
            "date": d,
            "memos": memos,
            "is_today": d == today,
            "is_weekend": d.weekday() >= 5
        })

    prev_month = month - 1 or 12
    prev_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year

    return templates.TemplateResponse(
        "calendar_month.html",
        {
            "request": request,
            "days": days,
            "year": year,
            "month": month,
            "prev_year": prev_year,
            "prev_month": prev_month,
            "next_year": next_year,
            "next_month": next_month
        }
    )
