[홈 메뉴 '달력' → 월간 달력 연결 (최소 패치)]
- 기존 기능/페이지 수정 없음
- 링크(href) 1줄만 변경

적용 방법(택1):
1) 홈/모바일 메뉴 템플릿에서
   <a href="/page/calendar">달력</a>
   를 찾아
   <a href="/page/calendar/month">달력</a>
   로 변경

2) 프로젝트 구조가 복잡한 경우:
   이 ZIP의 app/templates/menu_calendar_month_link.html 를 열어
   AFTER 블록의 한 줄만 그대로 복사해 붙여넣기

이유:
- /page/calendar/month 는 쿼리 없이 접속 시 오늘 월로 자동 이동
- 월간 달력 → 날짜 클릭 → 기존 상세(/page/calendar) 흐름 유지
