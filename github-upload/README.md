# 심사위원 챗봇

공공기관 바이브 코딩 검증용 Streamlit 앱입니다.  
**기획서 + README + 실행 코드(`app.py`)** 3가지를 입력하면 3대 분야 점수표와 평가 후기를 출력합니다.

## 3대 심사 분야

| 분야 | 평가 대상 |
|------|-----------|
| 공공기관 적합성 | 기획서 — 페인포인트·해결 방향·현장 적용 가능성 |
| 의도 구현도 | 기획서 ↔ 실행 코드 |
| README 품질 | README (규칙: `specs/README_RUBRIC.md`) |

## 입력·출력

- **입력:** 기획서, README, 실행 코드 (`app.py` 1개 권장)
- **출력:** 분야별·세부 점수표, 잘한 점 / 리스크 / 최종 한마디
- **Pass/Fail 없음** — 점수만 제공

## 사전 준비

- Python 3.10+
- OpenAI API 키 (모델: `gpt-4o` 고정)

## 설치 및 실행

```powershell
cd "c:\Users\menta\Desktop\심사위원 챗봇"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# .env에 OPENAI_API_KEY 설정
streamlit run app.py
```

## 프로젝트 구조

```
심사위원 챗봇/
├── app.py                      # Streamlit UI
├── judge/                      # 평가 로직
├── prompts/judge_system.txt    # 심사 프롬프트
└── specs/
    ├── PLAN.md                 # 앱 기획서
    └── README_RUBRIC.md        # README 평가 규칙
```

## 예시 데이터

| 세트 | 기획서 | README | 코드 |
|------|--------|--------|------|
| Pass 예상 | `examples/01_csv_dashboard/PLAN.md` | `examples/01_csv_dashboard/README.md` | `examples/01_csv_dashboard/app.py` |
| Fail 예상 | `examples/02_todo_tracker/PLAN.md` | `examples/02_todo_tracker/README.md` | `examples/02_todo_tracker/app.py` |

## 실행 코드 업로드 가이드

**단일 파일(`app.py`)만으로 충분한 경우:** 모든 로직이 한 파일에 있는 Streamlit 앱.

**추가 파일이 필요한 경우:** `judge/` 등 분리 모듈이 있으면 README에 구조·역할을 상세히 기재해야 합니다.  
모듈 코드 없이 README만으로는 **의도 구현도** 채점 정확도가 떨어질 수 있습니다.
