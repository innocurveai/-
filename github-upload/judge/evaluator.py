from pathlib import Path

from openai import APIError, OpenAI
from pydantic import ValidationError

from judge.models import EvaluationResult

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
