import html
import re

import streamlit as st

from judge.models import DOMAIN_LABELS, EvaluationResult

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def render_total_score(result: EvaluationResult) -> None:
    st.markdown(
        f"""
        <div class="score-hero">
            <span class="score-label">종합 점수</span>
            <span class="score-value">{result.total_score}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_domain_metrics(result: EvaluationResult) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric(DOMAIN_LABELS["public_sector"], result.public_sector_score)
    col2.metric(DOMAIN_LABELS["intent_implementation"], result.intent_implementation_score)
    col3.metric(DOMAIN_LABELS["readme_quality"], result.readme_quality_score)


def render_score_tables(result: EvaluationResult) -> None:
    st.subheader("분야별 점수")
    st.dataframe(
        result.domain_summary_rows(),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("세부 점수")
    st.dataframe(
        result.detail_score_rows(),
        use_container_width=True,
        hide_index=True,
    )


def _render_review_items(items: list[str], style: str) -> None:
    for item in items:
        safe_text = html.escape(item)
        st.markdown(
            f'<div class="review-item {style}">{safe_text}</div>',
            unsafe_allow_html=True,
        )


def _split_verdict_lines(text: str) -> list[str]:
    parts = [part.strip() for part in _SENTENCE_SPLIT.split(text.strip()) if part.strip()]
    if len(parts) >= 3:
        return parts[:3]
    if parts:
        return parts
    return [text.strip()]


def _format_verdict_html(text: str) -> str:
    lines = _split_verdict_lines(text)
    return "".join(
        f'<p class="verdict-line">{html.escape(line)}</p>' for line in lines
    )


def render_review(result: EvaluationResult) -> None:
    st.markdown('<p class="review-section-title">평가 후기</p>', unsafe_allow_html=True)

    col_strength, col_risk = st.columns(2, gap="medium")

    with col_strength:
        with st.container(border=True):
            st.markdown('<div class="review-accent-bar blue"></div>', unsafe_allow_html=True)
            st.markdown(
                '<p class="review-card-title positive">잘한 점</p>',
                unsafe_allow_html=True,
            )
            _render_review_items(result.strengths, "positive")

    with col_risk:
        with st.container(border=True):
            st.markdown('<div class="review-accent-bar rose"></div>', unsafe_allow_html=True)
            st.markdown(
                '<p class="review-card-title negative">감점 요인</p>',
                unsafe_allow_html=True,
            )
            _render_review_items(result.risks, "negative")

    st.markdown('<p class="review-verdict-title">최종 한마디</p>', unsafe_allow_html=True)

    _, verdict_col, _ = st.columns([1, 4, 1])
    with verdict_col:
        st.markdown(
            f'<div class="verdict-box">{_format_verdict_html(result.final_verdict)}</div>',
            unsafe_allow_html=True,
        )


def render_evaluation_result(result: EvaluationResult) -> None:
    if result.total_score == 0:
        st.warning(
            "입력된 기획서·README·코드가 심사 기준을 충족하지 않아 **전 항목 0점**으로 처리되었습니다."
        )
    render_total_score(result)
    render_domain_metrics(result)
    render_score_tables(result)
    render_review(result)
