[달력 월간보기 최소패치]
- 기존 기능/코드 수정 없음
- 신규 라우터 + 템플릿 + CSS만 추가

적용:
1) ZIP 풀어서 그대로 덮어쓰기
2) main.py에 아래 1줄만 추가
   from app.routers import calendar_month
   app.include_router(calendar_month.router)

URL:
/page/calendar/month?year=2025&month=12
