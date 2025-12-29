
PARS WMS 422 오류 + 입고/재고/이력 연결 FIX

해결 내용
1. 수기 입고 422 오류 해결 (Form name 일치)
2. 입고 시 inventory 자동 반영
3. 입고 시 history 자동 기록
4. 재고조회 / 이력조회 API 정상 데이터 반환

적용 방법
1. app/routers/inbound.py 교체
2. app/routers/inventory.py 교체
3. app/routers/history.py 교체
4. 서버 재시작
