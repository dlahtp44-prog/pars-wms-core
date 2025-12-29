
FINAL FIX 설명

현재 로그
- POST /api/inbound -> 422
- POST /api/inbound/excel -> 404

원인
1) /api/inbound
   - 화면은 FORM 전송
   - API가 JSON/다른 필드 기대 -> 422

2) /api/inbound/excel
   - router에 endpoint 미등록 or 다른 파일 사용 -> 404

해결
- inbound.py 하나에
  * FORM 기반 수기 입고
  * /excel 엔드포인트
  * inventory/history 동시 반영
  모두 통합

적용 방법
1. app/routers/inbound.py 교체
2. main.py 에서 inbound router include 확인
3. 서버 재시작
