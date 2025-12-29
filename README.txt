[달력 월간보기 간단 추가: 2번 + 4번]
- 기존 기능/페이지 수정 없음(달력 월간보기 파일만 교체)
- 2) 오늘 상세 버튼 추가: /page/calendar?date=YYYY-MM-DD
- 4) 오늘 자동 이동/포커스:
   - /page/calendar/month (쿼리 없이 접속) -> 오늘 월로 자동 이동
   - 오늘이 포함된 월에서는 자동으로 오늘 칸으로 스크롤

적용:
1) ZIP 풀어서 아래 파일 2개를 '그대로 덮어쓰기'
   - app/routers/calendar_month.py
   - app/templates/calendar_month.html
2) (이미 해두셨다면 생략) main.py 라우터 include 유지
   from app.routers import calendar_month
   app.include_router(calendar_month.router)

테스트:
- /page/calendar/month             (오늘 월로 자동 이동)
- /page/calendar/month?year=2025&month=12
