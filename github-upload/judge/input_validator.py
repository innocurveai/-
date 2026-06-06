"""분야별 입력 검증 — 해당 분야만 0점 처리."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

MIN_PLAN_CHARS = 80
MIN_README_CHARS = 60
MIN_CODE_CHARS = 40
MIN_PLAN_WORDS = 12
MIN_README_WORDS = 8
MIN_CODE_LINES = 2

PLAN_DOC_KEYWORDS = re.compile(
    r"요구|기능|목적|성공|기획|구현|UI|예외|범위|페인|문제|해결|기준|대시보드|앱",
    re.IGNORECASE,
)
PLAN_SOFTWARE_KEYWORDS = re.compile(
    r"앱|웹|web|시스템|소프트|streamlit|기능|구현|UI|코드|대시보드|업로드|API|실행|"
    r"app\.py|python|사용자|화면|입력|출력|파일|데이터|서비스|프로그램|개발",
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

TOPIC_SIGNALS = (
    "csv", "대시보드", "dashboard", "할일", "todo", "streamlit", "업로드", "upload",
    "포켓몬", "pokemon", "뉴스", "news", "정산", "영수증", "그래프", "chart",
)
OFF_TOPIC_PLAN = re.compile(r"포켓몬|pokemon", re.IGNORECASE)

WORD_PATTERN = re.compile(r"[\w가-힣]+", re.UNICODE)
LETTER_PATTERN = re.compile(r"[a-zA-Z가-힣]", re.UNICODE)
REPEAT_CHAR_PATTERN = re.compile(r"([a-zA-Z가-힣0-9])\1{7,}")

PLACEHOLDER_EXACT = {
    "안녕하세요", "안녕", "hello", "hi", "test", "테스트", "테스트 설명",
    "test description", "asdf", "qwerty", "123", "1234", "가나다", "바보",
    "바보 카카", "abc", "sample", "샘플", "예시", "입력", "내용", "코드",
    "기획서", "readme",
}


@dataclass
class DomainAssessment:
    """분야별 심사 가능 여부."""

    domain1_ok: bool = True
    domain1_reasons: list[str] = field(default_factory=list)
    domain2_ok: bool = True
    domain2_reasons: list[str] = field(default_factory=list)
    domain3_ok: bool = True
    domain3_reasons: list[str] = field(default_factory=list)
    all_fatal: bool = False
    fatal_reasons: list[str] = field(default_factory=list)


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
    if any(p in norm for p in ("테스트 설명", "test description", "안녕하세요")):
        if _word_count(text) < 25 and not README_KEYWORDS.search(text):
            return True
    return False


def _is_trivial_garbage(text: str) -> bool:
    stripped = text.strip()
    if not stripped or _is_placeholder(stripped):
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


def _topic_signals(text: str) -> set[str]:
    lowered = text.lower()
    return {signal for signal in TOPIC_SIGNALS if signal in lowered}


def _check_plan_for_domain1(plan_text: str) -> list[str]:
    issues: list[str] = []
    stripped = plan_text.strip()

    if _is_trivial_garbage(stripped):
        return ["기획서가 무의미한 입력입니다."]

    if len(stripped) < MIN_PLAN_CHARS or _word_count(stripped) < MIN_PLAN_WORDS:
        issues.append("기획서 내용이 너무 짧거나 실질 정보가 없습니다.")

    if not PLAN_DOC_KEYWORDS.search(stripped):
        issues.append("기획서 형식(요구사항·기능·성공 기준 등)이 아닙니다.")

    if not PLAN_SOFTWARE_KEYWORDS.search(stripped):
        issues.append(
            "소프트웨어·웹앱 개발 기획서가 아닙니다. "
            "(정책 아이디어·유머·코드 심사와 무관한 주제는 0점)"
        )

    if OFF_TOPIC_PLAN.search(stripped) and not re.search(
        r"streamlit|app\.py|UI|기능\s*\d|구현|API|대시보드\s*앱",
        stripped,
        re.IGNORECASE,
    ):
        issues.append("코드 심사와 무관한 주제(예: 포켓몬 도입)입니다.")

    return issues


def _check_readme_for_domain3(readme_text: str) -> list[str]:
    issues: list[str] = []
    stripped = readme_text.strip()

    if _is_trivial_garbage(stripped):
        return ["README가 무의미한 입력입니다."]

    if len(stripped) < MIN_README_CHARS or _word_count(stripped) < MIN_README_WORDS:
        issues.append("README 내용이 너무 짧습니다.")

    if not README_KEYWORDS.search(stripped):
        issues.append("README에 설치·실행·프로젝트 구조 안내가 없습니다.")

    return issues


def _check_code_for_domain2(code_text: str) -> list[str]:
    issues: list[str] = []
    stripped = code_text.strip()

    if _is_trivial_garbage(stripped):
        return ["실행 코드가 무의미한 입력입니다."]

    if len(stripped) < MIN_CODE_CHARS:
        issues.append("실행 코드가 너무 짧습니다.")

    if not CODE_KEYWORDS.search(stripped):
        issues.append("Python 실행 코드(import, def, streamlit 등)가 아닙니다.")

    if _line_count(stripped) < MIN_CODE_LINES and len(stripped) < 120:
        issues.append("실행 가능한 app.py 수준의 코드가 아닙니다.")

    return issues


def _check_plan_code_alignment(plan_text: str, code_text: str) -> list[str]:
    plan_topics = _topic_signals(plan_text)
    code_topics = _topic_signals(code_text)

    if plan_topics and code_topics and not (plan_topics & code_topics):
        return [
            "기획서와 실행 코드의 주제가 일치하지 않습니다. "
            f"(기획: {', '.join(sorted(plan_topics))} / 코드: {', '.join(sorted(code_topics))})"
        ]
    return []


def _check_readme_code_alignment(readme_text: str, code_text: str) -> list[str]:
    issues: list[str] = []
    code_lower = code_text.lower()
    readme_lower = readme_text.lower()

    if "streamlit" in code_lower and "streamlit" not in readme_lower:
        if not re.search(r"pip|실행|run|8501|app\.py", readme_lower):
            issues.append("README에 Streamlit 실행 안내가 없습니다.")

    readme_topics = _topic_signals(readme_text)
    code_topics = _topic_signals(code_text)
    if readme_topics and code_topics and not (readme_topics & code_topics):
        issues.append("README와 실행 코드가 서로 다른 프로젝트를 설명합니다.")

    return issues


def assess_domains(plan_text: str, readme_text: str, code_text: str) -> DomainAssessment:
    result = DomainAssessment()

    if not plan_text.strip() or not readme_text.strip() or not code_text.strip():
        result.all_fatal = True
        result.fatal_reasons = ["기획서, README, 실행 코드를 모두 입력해 주세요."]
        return result

    all_garbage = (
        _is_trivial_garbage(plan_text)
        and _is_trivial_garbage(readme_text)
        and _is_trivial_garbage(code_text)
    )
    if all_garbage:
        result.all_fatal = True
        result.fatal_reasons = ["세 입력 모두 무의미한 텍스트입니다."]
        return result

    d1 = _check_plan_for_domain1(plan_text)
    if d1:
        result.domain1_ok = False
        result.domain1_reasons = d1

    d3 = _check_readme_for_domain3(readme_text)
    readme_code = _check_readme_code_alignment(readme_text, code_text)
    if d3 or readme_code:
        result.domain3_ok = False
        result.domain3_reasons = d3 + readme_code

    d2_code = _check_code_for_domain2(code_text)
    d2_align = _check_plan_code_alignment(plan_text, code_text)
    d2_plan_min = []
    if _is_trivial_garbage(plan_text) or not PLAN_SOFTWARE_KEYWORDS.search(plan_text):
        d2_plan_min.append("기획서가 코드 심사용 개발 기획서가 아닙니다.")

    if d2_code or d2_align or d2_plan_min:
        result.domain2_ok = False
        result.domain2_reasons = d2_code + d2_align + d2_plan_min

    return result


def check_input_quality(plan_text: str, readme_text: str, code_text: str) -> list[str]:
    """전체 0점(구버전 호환) — all_fatal일 때만."""
    assessment = assess_domains(plan_text, readme_text, code_text)
    if assessment.all_fatal:
        return assessment.fatal_reasons
    return []
