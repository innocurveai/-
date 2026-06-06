"""심사위원 챗봇 — 바이브 코딩 검증 Streamlit 앱."""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from judge.evaluator import EvaluationError, run_evaluation
from judge.formatter import render_evaluation_result

load_dotenv()

PAGE_TITLE = "심사위원 챗봇"
PAGE_ICON = "⚖️"
MODEL = "gpt-4o"

GRADIENT_CSS = """
<style>
    .stApp {
        background: linear-gradient(
            145deg,
            #050508 0%,
            #0d1117 25%,
            #0a1628 50%,
            #1a0a12 75%,
            #120608 100%
        );
        background-attachment: fixed;
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background:
            radial-gradient(ellipse at 15% 20%, rgba(30, 100, 220, 0.18) 0%, transparent 55%),
            radial-gradient(ellipse at 85% 80%, rgba(220, 50, 60, 0.15) 0%, transparent 55%);
        pointer-events: none;
        z-index: 0;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"] {
        background: transparent;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1100px;
    }

    .hero-header {
        text-align: center;
        margin-bottom: 2.5rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid rgba(80, 130, 220, 0.15);
    }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.2;
        background: linear-gradient(90deg, #5eb3ff 0%, #c8d8ff 40%, #ff6b7a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.6rem 0;
    }

    .hero-subtitle {
        color: #8b9cb8;
        font-size: 1.05rem;
        font-weight: 400;
        letter-spacing: 0.04em;
        line-height: 1.5;
        margin: 0;
    }

    .input-panel-title {
        text-align: center;
        color: #6b7a94;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 0 0 1rem 0;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(
            160deg,
            rgba(18, 22, 36, 0.92) 0%,
            rgba(12, 14, 22, 0.88) 100%
        ) !important;
        border: 1px solid rgba(90, 130, 210, 0.18) !important;
        border-radius: 14px !important;
        padding: 0.25rem 0.5rem 0.5rem !important;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
        transition: border-color 0.2s, box-shadow 0.2s;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(100, 150, 240, 0.35) !important;
        box-shadow: 0 6px 28px rgba(30, 80, 180, 0.12);
    }

    .input-card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.85rem 0.6rem 0.65rem;
        border-bottom: 1px solid rgba(80, 120, 200, 0.12);
        margin-bottom: 0.5rem;
    }

    .input-card-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2.4rem;
        height: 2.4rem;
        border-radius: 10px;
        font-size: 1.15rem;
        flex-shrink: 0;
    }

    .accent-blue .input-card-icon {
        background: rgba(37, 99, 235, 0.18);
        border: 1px solid rgba(59, 130, 246, 0.35);
    }

    .accent-cyan .input-card-icon {
        background: rgba(6, 182, 212, 0.15);
        border: 1px solid rgba(34, 211, 238, 0.3);
    }

    .accent-rose .input-card-icon {
        background: rgba(220, 38, 38, 0.15);
        border: 1px solid rgba(248, 113, 113, 0.3);
    }

    .input-card-title {
        color: #e8eeff;
        font-size: 1.05rem;
        font-weight: 700;
        line-height: 1.3;
    }

    .input-card-hint {
        color: #6b7a94;
        font-size: 0.78rem;
        margin-top: 0.15rem;
        line-height: 1.3;
    }

    div[data-testid="stFileUploader"] {
        background: rgba(8, 10, 18, 0.55);
        border: 1px dashed rgba(80, 120, 200, 0.25);
        border-radius: 10px;
        padding: 0.4rem 0.6rem;
    }

    div[data-testid="stFileUploader"] label {
        color: #8b9cb8 !important;
        font-size: 0.82rem !important;
    }

    div[data-testid="stFileUploader"] small {
        color: #5a6880 !important;
    }

    div[data-testid="stFileUploader"] button {
        background: rgba(37, 99, 235, 0.15) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        color: #93c5fd !important;
        border-radius: 8px !important;
    }

    div[data-testid="stTextArea"] textarea {
        background: rgba(8, 10, 18, 0.65) !important;
        border: 1px solid rgba(80, 120, 200, 0.2) !important;
        border-radius: 10px !important;
        color: #dce6ff !important;
        font-size: 0.88rem !important;
    }

    div[data-testid="stTextArea"] textarea:focus {
        border-color: rgba(100, 150, 240, 0.45) !important;
        box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.2) !important;
    }

    div[data-testid="stTextArea"] textarea::placeholder {
        color: #4a5568 !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #2563eb 0%, #dc2626 100%);
        border: none;
        color: white;
        font-weight: 700;
        border-radius: 10px;
        padding: 0.65rem 2rem;
        transition: opacity 0.2s;
    }

    .stButton > button[kind="primary"]:hover {
        opacity: 0.88;
        border: none;
        color: white;
    }

    .score-hero {
        text-align: center;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            rgba(37, 99, 235, 0.2) 0%,
            rgba(20, 20, 30, 0.6) 50%,
            rgba(220, 38, 38, 0.18) 100%
        );
        border: 1px solid rgba(100, 140, 255, 0.3);
    }

    .score-label {
        display: block;
        color: #9aa8c4;
        font-size: 0.95rem;
        margin-bottom: 0.3rem;
    }

    .score-value {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #f87171);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .verdict-box {
        background: linear-gradient(
            160deg,
            rgba(37, 99, 235, 0.12) 0%,
            rgba(20, 25, 40, 0.85) 45%,
            rgba(220, 38, 38, 0.1) 100%
        );
        border: 1px solid rgba(100, 140, 255, 0.25);
        padding: 1.2rem 1.6rem;
        border-radius: 14px;
        max-width: 680px;
        margin: 0 auto;
    }

    .verdict-line {
        color: #e8eeff;
        font-size: 0.95rem;
        line-height: 1.75;
        text-align: center !important;
        margin: 0.4rem 0;
    }

    .review-verdict-title {
        display: block;
        width: 100%;
        text-align: center !important;
        font-size: 1.2rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        margin: 1.5rem 0 0.85rem;
        background: linear-gradient(90deg, #93c5fd 0%, #e8eeff 50%, #fca5a5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .review-section-title {
        text-align: center;
        color: #e8eeff;
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        margin: 1.25rem 0 1rem;
    }

    .review-accent-bar {
        height: 3px;
        border-radius: 4px;
        margin-bottom: 0.75rem;
    }

    .review-accent-bar.blue { background: #3b82f6; }
    .review-accent-bar.rose { background: #ef4444; }

    .review-card-title {
        color: #e8eeff;
        font-size: 0.92rem;
        font-weight: 700;
        margin: 0 0 0.75rem 0;
    }

    .review-card-title.positive { color: #93c5fd; }
    .review-card-title.negative { color: #fca5a5; }

    .review-item {
        padding: 0.6rem 0.8rem;
        margin-bottom: 0.45rem;
        border-radius: 8px;
        font-size: 0.85rem;
        line-height: 1.55;
        color: #c8d4ec;
    }

    .review-item.positive {
        background: rgba(37, 99, 235, 0.1);
        border-left: 3px solid #3b82f6;
    }

    .review-item.negative {
        background: rgba(220, 38, 38, 0.1);
        border-left: 3px solid #ef4444;
    }

    [data-testid="stMetric"] {
        background: rgba(15, 18, 30, 0.7);
        border: 1px solid rgba(80, 120, 200, 0.2);
        border-radius: 10px;
        padding: 0.8rem 1rem;
    }

    [data-testid="stMetricLabel"] {
        color: #9aa8c4 !important;
    }

    [data-testid="stMetricValue"] {
        background: linear-gradient(90deg, #93c5fd, #fca5a5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(12, 14, 22, 0.6);
        border-radius: 12px;
        padding: 0.35rem;
        border: 1px solid rgba(80, 120, 200, 0.15);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #6b7a94;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, rgba(37, 99, 235, 0.25), rgba(220, 38, 38, 0.2)) !important;
        color: #e8eeff !important;
    }

    .criteria-intro {
        text-align: center;
        width: 100%;
        margin: 0.5rem auto 2rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .criteria-intro-label {
        color: #6b7a94;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
        text-align: center;
        width: 100%;
    }

    .criteria-intro-desc {
        color: #9aa8c4;
        font-size: 0.92rem;
        line-height: 1.7;
        text-align: center;
        width: 100%;
        margin: 0;
    }

    .criteria-accent-bar {
        height: 3px;
        border-radius: 4px;
        margin-bottom: 0.85rem;
    }

    .criteria-accent-bar.blue { background: #3b82f6; }
    .criteria-accent-bar.mix  { background: linear-gradient(90deg, #3b82f6, #ef4444); }
    .criteria-accent-bar.rose { background: #ef4444; }

    .criteria-domain-num {
        color: #6b7a94;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin: 0 0 0.25rem 0;
    }

    .criteria-domain-title {
        color: #e8eeff !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        margin: 0 0 0.35rem 0 !important;
        padding: 0 !important;
    }

    .criteria-domain-source {
        display: inline-block;
        font-size: 0.72rem;
        color: #8b9cb8;
        background: rgba(80, 120, 200, 0.1);
        border: 1px solid rgba(80, 120, 200, 0.15);
        border-radius: 20px;
        padding: 0.15rem 0.6rem;
        margin-bottom: 0.25rem;
    }

    .criteria-item-title {
        color: #c8d4ec !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        margin: 0.65rem 0 0.15rem 0 !important;
    }

    .criteria-item-desc {
        color: #6b7a94 !important;
        font-size: 0.8rem !important;
        line-height: 1.5 !important;
        margin: 0 0 0.5rem 0 !important;
    }

    .criteria-footer {
        text-align: center;
        padding: 1rem 1.5rem;
        background: rgba(12, 14, 22, 0.5);
        border: 1px solid rgba(80, 120, 200, 0.12);
        border-radius: 10px;
        color: #6b7a94;
        font-size: 0.82rem;
        line-height: 1.5;
        width: 100%;
        box-sizing: border-box;
    }

    .criteria-footer strong {
        color: #93c5fd;
        font-weight: 600;
    }
</style>
"""

CRITERIA_DOMAINS = [
    {
        "num": "01",
        "title": "공공기관 적합성",
        "source": "기획서",
        "accent": "blue",
        "items": [
            ("페인포인트 명확성", "행정·현장·민원 맥락에서 문제가 구체적으로 드러나는지"),
            ("해결 방향 적절성", "제안 기능이 실제 업무 부담을 줄이는지"),
            ("공공 현장 적용 가능성", "보안·예산·조직 환경에서 실행 가능한지"),
        ],
    },
    {
        "num": "02",
        "title": "의도 구현도",
        "source": "기획서 ↔ 실행 코드",
        "accent": "mix",
        "items": [
            ("핵심 요구사항 구현", "기획서의 필수 기능이 코드에 반영되었는지"),
            ("성공 기준 충족", "UI·예외 처리 등 명시된 기준을 지켰는지"),
            ("기획 의도 일치", "핵심 의도가 왜곡·누락되지 않았는지 (합리적 구현 보완은 감점 아님)"),
        ],
    },
    {
        "num": "03",
        "title": "README 품질",
        "source": "README",
        "accent": "rose",
        "items": [
            ("설치 · 실행 안내", "문서만으로 환경 구성·실행이 가능한지"),
            ("기획 · 코드 정합성", "README 설명이 기획서·코드와 일치하는지"),
            ("유지보수 · 확장 가이드", "구조·파일 역할·확장 방법이 명확한지"),
        ],
    },
]


def configure_page() -> None:
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(GRADIENT_CSS, unsafe_allow_html=True)


def read_uploaded_text(uploaded_file) -> str:
    raw = uploaded_file.read()
    if isinstance(raw, bytes):
        return raw.decode("utf-8", errors="replace")
    return str(raw)


def resolve_text(text_input: str, uploaded_file) -> str:
    if uploaded_file is not None:
        return read_uploaded_text(uploaded_file)
    return text_input


UPLOAD_FIELDS = [
    {
        "key": "plan",
        "icon": "📋",
        "title": "기획서",
        "hint": "요구사항 · 성공 기준",
        "file_label": "파일 선택 (.md, .txt)",
        "file_types": ["md", "txt"],
        "placeholder": "기획서 내용을 붙여넣으세요.",
        "accent": "blue",
    },
    {
        "key": "readme",
        "icon": "📄",
        "title": "README",
        "hint": "설치 · 실행 · 구조 안내",
        "file_label": "파일 선택 (.md, .txt)",
        "file_types": ["md", "txt"],
        "placeholder": "README 내용을 붙여넣으세요.",
        "accent": "cyan",
    },
    {
        "key": "code",
        "icon": "⚙️",
        "title": "실행 코드",
        "hint": "진입점 app.py",
        "file_label": "파일 선택 (.py)",
        "file_types": ["py"],
        "placeholder": "실행 코드를 붙여넣으세요.",
        "accent": "rose",
    },
]


def render_upload_card(field: dict) -> tuple[str, object]:
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="input-card-header accent-{field['accent']}">
                <span class="input-card-icon">{field['icon']}</span>
                <div>
                    <div class="input-card-title">{field['title']}</div>
                    <div class="input-card-hint">{field['hint']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded = st.file_uploader(
            field["file_label"],
            type=field["file_types"],
            key=f"{field['key']}_upload",
            label_visibility="collapsed",
        )
        text = st.text_area(
            "직접 입력",
            height=140,
            key=f"{field['key']}_text",
            label_visibility="collapsed",
            placeholder=field["placeholder"],
        )
    return text, uploaded


def render_evaluate_tab() -> None:
    st.markdown('<p class="input-panel-title">심사 자료</p>', unsafe_allow_html=True)
    st.caption(
        "README와 실행 코드(app.py)는 동일한 프로젝트를 설명하도록 맞춰 제출해 주시면 "
        "보다 정확한 심사가 가능합니다. 세 분야는 각각 독립적으로 평가됩니다."
    )

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        plan_text, plan_upload = render_upload_card(UPLOAD_FIELDS[0])
    with col2:
        readme_text, readme_upload = render_upload_card(UPLOAD_FIELDS[1])
    with col3:
        code_text, code_upload = render_upload_card(UPLOAD_FIELDS[2])

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("심사 시작", type="primary", use_container_width=True):
        resolved_plan = resolve_text(plan_text, plan_upload)
        resolved_readme = resolve_text(readme_text, readme_upload)
        resolved_code = resolve_text(code_text, code_upload)
        api_key = os.getenv("OPENAI_API_KEY", "")

        try:
            with st.spinner("심사위원이 평가 중입니다..."):
                result = run_evaluation(
                    resolved_plan,
                    resolved_readme,
                    resolved_code,
                    api_key=api_key,
                    model=MODEL,
                )
            st.divider()
            render_evaluation_result(result)
        except EvaluationError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"예상치 못한 오류가 발생했습니다: {exc}")


def render_criteria_domain(domain: dict) -> None:
    with st.container(border=True):
        st.markdown(
            f'<div class="criteria-accent-bar {domain["accent"]}"></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="criteria-domain-num">분야 {domain["num"]}</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="criteria-domain-title">{domain["title"]}</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<span class="criteria-domain-source">{domain["source"]}</span>',
            unsafe_allow_html=True,
        )
        st.divider()
        for idx, (name, desc) in enumerate(domain["items"], start=1):
            st.markdown(f"**{idx}. {name}**")
            st.caption(desc)


def render_criteria_tab() -> None:
    _, intro_col, _ = st.columns([1, 3, 1])
    with intro_col:
        st.markdown(
            """
            <div class="criteria-intro">
                <div class="criteria-intro-label">채점 체계</div>
                <p class="criteria-intro-desc">
                    3개 분야 · 9개 세부 항목 · 항목당 0–100점<br>
                    분야 점수는 세부 항목 평균, 종합 점수는 3개 분야 평균입니다.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        render_criteria_domain(CRITERIA_DOMAINS[0])
    with col2:
        render_criteria_domain(CRITERIA_DOMAINS[1])
    with col3:
        render_criteria_domain(CRITERIA_DOMAINS[2])

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="criteria-footer">
            README 세부 채점 규칙은 <strong>specs/README_RUBRIC.md</strong>를 따릅니다.<br>
            심사 결과는 점수와 후기만 제공하며, 수정 코드·디버깅 가이드는 포함하지 않습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    configure_page()

    st.markdown(
        f"""
        <div class="hero-header">
            <h1 class="hero-title">{PAGE_ICON} {PAGE_TITLE}</h1>
            <p class="hero-subtitle">공공기관 적합성 · 의도 구현도 · README 품질 — 3대 분야 심사</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-your"):
        st.warning("OPENAI_API_KEY가 .env에 설정되지 않았습니다.")

    tab_evaluate, tab_criteria = st.tabs(["채점", "채점 기준"])

    with tab_evaluate:
        render_evaluate_tab()

    with tab_criteria:
        render_criteria_tab()


if __name__ == "__main__":
    main()
