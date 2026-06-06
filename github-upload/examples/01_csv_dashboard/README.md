# CSV 요약 대시보드

CSV 파일을 업로드하면 숫자 컬럼의 핵심 지표와 막대 그래프를 보여 주는 Streamlit 앱입니다.

## 실행 방법

```powershell
pip install streamlit pandas
streamlit run app.py
```

브라우저: http://localhost:8501

## 기능

- CSV 파일 1개 업로드
- 숫자형 컬럼별 평균·합계·최대값 Metrics
- 첫 번째 숫자 컬럼 기준 상위 10행 막대 차트
- Sidebar: 파일명, 행·열 개수

## 프로젝트 구조

```
app.py    # Streamlit 진입점 (단일 파일)
```

## 예외 처리

- 파일 미업로드 → 안내 메시지
- CSV 파싱 실패 → 에러 메시지
- 숫자 컬럼 없음 → 안내 메시지

## 범위 외

- DB, 로그인, API 연동, 다중 파일 비교
