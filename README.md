진짜 수정본 (한 번에 끝내기)

해결되는 증상
1) 재고조회: 품번/브랜드/비고가 비어있음  -> ✅ 입고 시 저장 + 조회 반영
2) 이력조회: 로케이션/품번/브랜드/업데이트/시간이 비어있음 -> ✅ history 저장/조회 반영
3) 이력조회 엑셀 다운로드 없음 -> ✅ /api/history/excel 생성
+ 재고조회 엑셀 다운로드 -> ✅ /api/inventory/excel 생성

핵심 원인
- DB(stock/history)에 brand/memo/updated_at 컬럼이 없거나
- 입고 시점에 저장하지 않아서 조회해도 NULL

이 패치의 내용
- init_db()에서 자동 마이그레이션:
  stock: brand, memo 컬럼 추가
  history: brand, updated_at 컬럼 추가
- 수기/엑셀 입고 시 stock/history에 brand/memo/updated_at 저장
- /page/inventory, /page/history 쿼리 교정(깨진 "...ts" 포함)
- inventory/history 엑셀 다운로드(xlsx) 엔드포인트 추가
- 템플릿을 캡처 형태(엑셀 시트형)로 교체 + 다운로드 링크 추가

적용 방법
1) 이 ZIP 압축 해제
2) 프로젝트에 아래 파일들 "그대로 덮어쓰기"
   - app/main.py
   - app/templates/inbound.html
   - app/templates/inventory.html
   - app/templates/history.html
   - requirements.txt
3) 배포/재시작

정상 확인
- 입고 시 브랜드/비고 입력 -> 재고조회에 바로 표시
- 이력조회에 구분/로케이션/품번/브랜드/업데이트/시간 표시
- 재고/이력 엑셀 다운로드 클릭 시 xlsx 다운로드
