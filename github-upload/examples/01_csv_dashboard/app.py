"""CSV 요약 대시보드 — 기획서 충실 구현 예시 (Pass 예상)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

PAGE_TITLE = "CSV 요약 대시보드"
TOP_N_ROWS = 10


def configure_page() -> None:
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")


def load_csv(uploaded_file) -> pd.DataFrame | None:
    try:
        return pd.read_csv(uploaded_file)
    except Exception as exc:
        st.error(f"CSV 파싱 실패: {exc}")
        return None


def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()


def render_sidebar(df: pd.DataFrame, filename: str) -> None:
    with st.sidebar:
        st.header("파일 정보")
        st.write(f"파일명: {filename}")
        st.write(f"행: {len(df):,}")
        st.write(f"열: {len(df.columns):,}")


def render_metrics(df: pd.DataFrame, numeric_cols: list[str]) -> None:
    st.subheader("숫자 컬럼 요약")
    for col in numeric_cols:
        series = df[col].dropna()
        c1, c2, c3 = st.columns(3)
        c1.metric(f"{col} 평균", f"{series.mean():,.2f}")
        c2.metric(f"{col} 합계", f"{series.sum():,.2f}")
        c3.metric(f"{col} 최대", f"{series.max():,.2f}")


def render_bar_chart(df: pd.DataFrame, numeric_cols: list[str]) -> None:
    target_col = numeric_cols[0]
    st.subheader(f"막대 그래프 — {target_col} (상위 {TOP_N_ROWS}행)")
    chart_df = df.nlargest(TOP_N_ROWS, target_col)[[target_col]]
    st.bar_chart(chart_df)


def main() -> None:
    configure_page()
    st.title(PAGE_TITLE)

    uploaded = st.file_uploader("CSV 파일 업로드", type=["csv"])
    if uploaded is None:
        st.info("CSV 파일을 업로드해 주세요.")
        return

    df = load_csv(uploaded)
    if df is None:
        return

    render_sidebar(df, uploaded.name)

    numeric_cols = get_numeric_columns(df)
    if not numeric_cols:
        st.warning("숫자형 컬럼이 없습니다.")
        return

    render_metrics(df, numeric_cols)
    render_bar_chart(df, numeric_cols)


if __name__ == "__main__":
    main()
