
요구사항 반영 ZIP

1. 입고 등록
- 수기 / 엑셀 입고를 시트처럼 구분

2. 재고 조회
- updated_at(업데이트 날짜) 노출

3. 이력 조회
- 구분(type): 입고/출고/이동
- 출발(src) / 도착(dst) 로케이션 포함

적용
- app/templates/inbound.html 교체
- app/routers/inventory.py 교체
- app/routers/history.py 교체
