의존성 보완 수정 ZIP

문제 원인
- inbound.py 에서 pandas 사용
- requirements.txt 에 pandas 누락
- 앱 로딩 단계에서 ModuleNotFoundError 발생

해결
- pandas + openpyxl 추가
- 기능 변경 없음

적용 방법
1. requirements.txt 교체
2. Railway Redeploy
