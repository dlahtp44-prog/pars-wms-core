
🔥 REAL FIX - router include 문제

증상
- POST /api/inbound -> 422 (body.item missing)

진짜 원인
- main.py 에서 api_inbound(router)가 include 되어 있었음
- 그래서 JSON body(item) 요구하는 옛 API가 실행됨

해결
- api_inbound 사용 중단
- inbound(Form 기반)만 include

적용
1. 이 ZIP의 main.py 로 교체
2. app/routers/api_inbound.py 제거 또는 미사용
3. 서버 재시작

정상
- /api/inbound 직접 접속 시 405
- 수기 입고 정상
- 엑셀 입고 정상
- 재고/이력 반영
