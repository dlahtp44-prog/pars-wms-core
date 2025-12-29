
재고/이력 필드 누락 + 이력 엑셀 다운로드 FIX

해결 내용
1. inventory 조회
- 품번(item_code), 브랜드(brand), 비고(memo) 누락 수정

2. history 조회
- 로케이션, 품번, 브랜드, 업데이트(updated_at) 누락 수정

3. history 엑셀 다운로드
- /api/history/excel 추가

적용
- app/routers/inventory.py 교체
- app/routers/history.py 교체
- 서버 재시작
