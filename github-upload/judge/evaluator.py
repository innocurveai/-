from pathlib import Path

from openai import APIError, OpenAI
from pydantic import ValidationError

from judge.models import EvaluationResult
from judge.input_validator import check_input_quality

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
SPECS_DIR = Path(__file__).resolve().parent.parent / "specs"
DEFAULT_MODEL = "gpt-4o"


class EvaluationError(Exception):
    """평가 과정에서 발생한 사용자 대면 오류."""


def load_system_prompt() -> str:
    template_path = PROMPTS_DIR / "judge_system.txt"
    rubric_path = SPECS_DIR / "README_RUBRIC.md"

    if not template_path.exists():
        raise EvaluationError(f"시스템 프롬프트 파일을 찾을 수 없습니다: {template_path}")
    if not rubric_path.exists():
        raise EvaluationError(f"README 평가 규칙 파일을 찾을 수 없습니다: {rubric_path}")

    template = template_path.read_text(encoding="utf-8")
    rubric = rubric_path.read_text(encoding="utf-8")
    return template.replace("{readme_rubric}", rubric)


def build_user_message(plan_text: str, readme_text: str, code_text: str) -> str:
    return (
        f"## 기획서\n{plan_text.strip()}\n\n"
        f"## README\n{readme_text.strip()}\n\n"
        f"## 실행 코드\n{code_text.strip()}"
    )


def build_zero_evaluation(issues: list[str]) -> EvaluationResult:
    """무의미·불충분 입력 — 전 항목 0점."""
    unique_issues = list(dict.fromkeys(issues))[:5]
    return EvaluationResult(
        pain_point_clarity=0,
        solution_appropriateness=0,
        public_feasibility=0,
        requirement_coverage=0,
        success_criteria_met=0,
        fidelity_no_bloat=0,
        setup_instructions=0,
        documentation_accuracy=0,
        maintainability=0,
        strengths=[
            "제출된 자료만으로는 심사할 수 있는 기획·문서·코드 내용이 확인되지 않았습니다."
        ],
        risks=unique_issues if unique_issues else ["실제 기획서, README, 실행 코드를 제출해 주세요."],
        final_verdict=(
            "이번 제출은 심사 기준을 충족하지 않아 모든 항목 0점으로 처리했습니다. "
            "기획서·README·app.py를 준비해 주시면 더 정확한 평가를 받으실 수 있습니다. "
            "다음 제출을 기대하겠습니다."
        ),
    )


def validate_inputs(plan_text: str, readme_text: str, code_text: str) -> None:
    if not plan_text.strip():
        raise EvaluationError("기획서를 입력해 주세요.")
    if not readme_text.strip():
        raise EvaluationError("README 파일을 입력해 주세요.")
    if not code_text.strip():
        raise EvaluationError("실행 코드(app.py)를 입력해 주세요.")


def run_evaluation(
    plan_text: str,
    readme_text: str,
    code_text: str,
    *,
    api_key: str,
    model: str = DEFAULT_MODEL,
) -> EvaluationResult:
    validate_inputs(plan_text, readme_text, code_text)

    quality_issues = check_input_quality(plan_text, readme_text, code_text)
    if quality_issues:
        return build_zero_evaluation(quality_issues)

    if not api_key.strip():
        raise EvaluationError(
            "OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해 주세요."
        )

    client = OpenAI(api_key=api_key)
    system_prompt = load_system_prompt()
    user_message = build_user_message(plan_text, readme_text, code_text)

    try:
        response = client.responses.parse(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            text_format=EvaluationResult,
        )
    except APIError as exc:
        raise EvaluationError(f"OpenAI API 오류: {exc}") from exc

    parsed = response.output_parsed
    if parsed is None:
        raise EvaluationError("평가 결과를 파싱하지 못했습니다. 다시 시도해 주세요.")

    try:
        return EvaluationResult.model_validate(parsed)
    except ValidationError as exc:
        raise EvaluationError(f"평가 결과 형식이 올바르지 않습니다: {exc}") from exc
