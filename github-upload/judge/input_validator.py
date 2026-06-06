"""기획서·README·코드 입력 품질 검증 — 미달 시 0점 처리."""

from __future__ import annotations

import re

MIN_PLAN_CHARS = 80
MIN_README_CHARS = 60
MIN_CODE_CHARS = 40
MIN_PLAN_WORDS = 12
MIN_README_WORDS = 8
MIN_CODE_LINES = 2

PLAN_KEYWORDS = re.compile(
    r"요구|기능|목적|성공|기획|구현|UI|예외|범위|페인|문제|해결|기준|대시보드|앱",
    re.IGNORECASE,
)
README_KEYWORDS = re.compile(
    r"설치|실행|streamlit|pip|python|app\.py|프로젝트|readme|requirements|구조|환경|venv",
    re.IGNORECASE,
)
CODE_KEYWORDS = re.compile(
    r"\b(import|def|class|streamlit|st\.|if __name__|return|try|except|for|while)\b",
    re.IGNORECASE,
)
WORD_PATTERN = re.compile(r"[\w가-힣]+", re.UNICODE)
LETTER_PATTERN = re.compile(r"[a-zA-Z가-힣]", re.UNICODE)
REPEAT_CHAR_PATTERN = re.compile(r"(.)\1{7,}")

PLACEHOLDER_EXACT = {
    "안녕하세요",
    "안녕",
    "hello",
    "hi",
    "test",
    "테스트",
    "테스트 설명",
    "test description",
    "asdf",
    "qwerty",
    "123",
    "1234",
    "가나다",
    "바보",
    "바보 카카",
    "abc",
    "sample",
    "샘플",
    "예시",
    "입력",
    "내용",
    "코드",
    "기획서",
    "readme",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _word_count(text: str) -> int:
    return len(WORD_PATTERN.findall(text))


def _line_count(text: str) -> int:
    return len([line for line in text.splitlines() if line.strip()])


def _letter_ratio(text: str) -> float:
    stripped = text.strip()
    if not stripped:
        return 0.0
    return len(LETTER_PATTERN.findall(stripped)) / len(stripped)


def _is_placeholder(text: str) -> bool:
    norm = _normalize(text)
    if norm in PLACEHOLDER_EXACT:
        return True
    if len(norm) <= 30 and any(norm == p or norm.startswith(p + " ") for p in PLACEHOLDER_EXACT):
        return True
    return False


def _is_trivial_garbage(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if _is_placeholder(stripped):
        return True
    if REPEAT_CHAR_PATTERN.search(stripped):
        return True
    if re.fullmatch(r"[\d\s\W]+", stripped):
        return True
    words = WORD_PATTERN.findall(stripped)
    if not words:
        return True
    if len(set(words)) <= 2 and len(words) >= 3:
        return True
    return False


def _check_document(
    text: str,
    *,
    label: str,
    min_chars: int,
    min_words: int,
    keyword_pattern: re.Pattern[str],
) -> list[str]:
    issues: list[str] = []
    stripped = text.strip()

    if len(stripped) < min_chars:
        issues.append(f"{label} 내용이 너무 짧거나 실질 정보가 없습니다.")

    if _is_trivial_garbage(stripped):
        issues.append(f"{label}가 인사·테스트 문구 등 무의미한 입력으로 보입니다.")

    if _word_count(stripped) < min_words:
        issues.append(f"{label}에 요구사항·설명 등 실질 문장이 부족합니다.")

    if _letter_ratio(stripped) < 0.25:
        issues.append(f"{label} 형식이 올바르지 않습니다.")

    if not keyword_pattern.search(stripped):
        issues.append(f"{label}로 인식하기 어렵습니다. 실제 {label} 파일 내용을 제출해 주세요.")

    return issues


def _check_code(text: str) -> list[str]:
    issues: list[str] = []
    stripped = text.strip()
    label = "실행 코드"

    if len(stripped) < MIN_CODE_CHARS:
        issues.append(f"{label}가 너무 짧습니다.")

    if _is_trivial_garbage(stripped):
        issues.append(f"{label}가 Python 소스가 아닌 무의미한 텍스트입니다.")

    if not CODE_KEYWORDS.search(stripped):
        issues.append(f"{label}에 import, def, streamlit 등 Python 코드 요소가 없습니다.")

    if _line_count(stripped) < MIN_CODE_LINES and len(stripped) < 120:
        issues.append(f"{label}가 실행 가능한 app.py 수준의 코드가 아닙니다.")

    return issues


def check_input_quality(plan_text: str, readme_text: str, code_text: str) -> list[str]:
    """심사 불가 입력이면 사유 목록 반환. 빈 목록이면 정상."""
    issues: list[str] = []
    issues.extend(
        _check_document(
            plan_text,
            label="기획서",
            min_chars=MIN_PLAN_CHARS,
            min_words=MIN_PLAN_WORDS,
            keyword_pattern=PLAN_KEYWORDS,
        )
    )
    issues.extend(
        _check_document(
            readme_text,
            label="README",
            min_chars=MIN_README_CHARS,
            min_words=MIN_README_WORDS,
            keyword_pattern=README_KEYWORDS,
        )
    )
    issues.extend(_check_code(code_text))
    return issues
