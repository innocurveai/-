"""할 일 관리 보드 — 기획서와 어긋난 구현 예시 (Fail/감점 예상)."""

import streamlit as st

# 기획서에 없는 기능: 우선순위·DB 연동 스텁
PRIORITY_LEVELS = ["낮음", "보통", "높음"]


def configure_page() -> None:
    st.set_page_config(page_title="Todo App", layout="centered")


def add_todo(text: str) -> None:
    # session_state 미사용 → 새로고침 시 목록 소실 (기획 위반)
    if "todos" not in st.session_state:
        st.session_state.todos = []
    st.session_state.todos.append({"text": text, "done": False})


def main() -> None:
    configure_page()
    st.title("My Todo")  # 기획서 제목과 불일치

    # 기획서 요구 Tabs/Sidebar Metrics 없음
    st.subheader("할 일 추가")
    new_todo = st.text_input("할 일")
    priority = st.selectbox("우선순위", PRIORITY_LEVELS)  # 범위外 기능

    if st.button("추가"):
        add_todo(f"[{priority}] {new_todo}")  # 빈 문자열도 그대로 추가 (예외 처리 없음)

    st.subheader("전체 목록")
    todos = st.session_state.get("todos", [])
    for idx, item in enumerate(todos):
        st.write(f"{idx + 1}. {item['text']}")

    # 완료 체크박스·완료 탭 미구현
    st.caption("DB sync placeholder")  # 기획에 없는 잔재 코드


if __name__ == "__main__":
    main()
