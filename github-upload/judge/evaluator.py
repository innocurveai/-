from pathlib import Path

from openai import APIError, OpenAI
from pydantic import ValidationError

from judge.domain_models import (
    IntentScores,
    PublicSectorScores,
    ReadmeScores,
    ReviewSummary,
)
from judge.input_validator import DomainAssessment, assess_domains
from judge.models import EvaluationResult

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
SPECS_DIR = Path(__file__).resolve().parent.parent / "specs"
DEFAULT_MODEL = "gpt-4o"


class EvaluationError(Exception):
    """평가 과정에서 발생한 사용자 대면 오류."""


def _load_prompt(filename: str, *, readme_rubric: str = "") -> str:
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise EvaluationError(f"프롬프트 파일을 찾을 수 없습니다: {path}")
    text = path.read_text(encoding="utf-8")
    return text.replace("{readme_rubric}", readme_rubric)


def _load_readme_rubric() -> str:
    path = SPECS_DIR / "README_RUBRIC.md"
    if not path.exists():
        raise EvaluationError(f"README 평가 규칙 파일을 찾을 수 없습니다: {path}")
    return path.read_text(encoding="utf-8")


def _call_domain(client: OpenAI, model: str, system: str, user: str, schema: type):
    response = client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        text_format=schema,
    )
    parsed = response.output_parsed
    if parsed is None:
        raise EvaluationError("평가 결과를 파싱하지 못했습니다.")
    return schema.model_validate(parsed)


def build_zero_evaluation(issues: list[str]) -> EvaluationResult:
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
        strengths=["제출된 자료만으로는 심사할 수 있는 내용이 확인되지 않았습니다."],
        risks=unique_issues if unique_issues else ["실제 기획서, README, 실행 코드를 제출해 주세요."],
        final_verdict=(
            "이번 제출은 심사 기준을 충족하지 않아 모든 항목 0점으로 처리했습니다. "
            "기획서·README·app.py를 서로 연관되게 준비해 주시면 정확한 평가가 가능합니다. "
            "다음 제출을 기대하겠습니다."
        ),
    )


def _zero_public() -> PublicSectorScores:
    return PublicSectorScores(
        pain_point_clarity=0,
        solution_appropriateness=0,
        public_feasibility=0,
    )


def _zero_intent() -> IntentScores:
    return IntentScores(
        requirement_coverage=0,
        success_criteria_met=0,
        fidelity_no_bloat=0,
    )


def _zero_readme() -> ReadmeScores:
    return ReadmeScores(
        setup_instructions=0,
        documentation_accuracy=0,
        maintainability=0,
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

    assessment = assess_domains(plan_text, readme_text, code_text)
    if assessment.all_fatal:
        return build_zero_evaluation(assessment.fatal_reasons)

    if not api_key.strip():
        raise EvaluationError(
            "OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해 주세요."
        )

    client = OpenAI(api_key=api_key)
    readme_rubric = _load_readme_rubric()
    plan = plan_text.strip()
    readme = readme_text.strip()
    code = code_text.strip()

    try:
        if assessment.domain1_ok:
            public = _call_domain(
                client,
                model,
                _load_prompt("domain1_public.txt"),
                f"## 기획서\n{plan}",
                PublicSectorScores,
            )
        else:
            public = _zero_public()

        if assessment.domain2_ok:
            intent = _call_domain(
                client,
                model,
                _load_prompt("domain2_intent.txt"),
                f"## 기획서\n{plan}\n\n## 실행 코드\n{code}",
                IntentScores,
            )
        else:
            intent = _zero_intent()

        if assessment.domain3_ok:
            readme_scores = _call_domain(
                client,
                model,
                _load_prompt("domain3_readme.txt", readme_rubric=readme_rubric),
                f"## README\n{readme}\n\n## 기획서\n{plan}\n\n## 실행 코드\n{code}",
                ReadmeScores,
            )
        else:
            readme_scores = _zero_readme()

        scores_snapshot = {
            "공공기관 적합성": public.model_dump(),
            "의도 구현도": intent.model_dump(),
            "README 품질": readme_scores.model_dump(),
            "domain1_skipped": not assessment.domain1_ok,
            "domain2_skipped": not assessment.domain2_ok,
            "domain3_skipped": not assessment.domain3_ok,
            "skip_reasons": {
                "domain1": assessment.domain1_reasons,
                "domain2": assessment.domain2_reasons,
                "domain3": assessment.domain3_reasons,
            },
        }

        review = _call_domain(
            client,
            model,
            _load_prompt("review_summary.txt"),
            (
                f"## 기획서\n{plan}\n\n## README\n{readme}\n\n## 실행 코드\n{code}\n\n"
                f"## 산출 점수\n{scores_snapshot}"
            ),
            ReviewSummary,
        )
    except APIError as exc:
        raise EvaluationError(f"OpenAI API 오류: {exc}") from exc
    except ValidationError as exc:
        raise EvaluationError(f"평가 결과 형식이 올바르지 않습니다: {exc}") from exc

    risks = list(review.risks)
    for label, reasons in (
        ("[기획서 0점]", assessment.domain1_reasons),
        ("[의도구현 0점]", assessment.domain2_reasons),
        ("[README 0점]", assessment.domain3_reasons),
    ):
        if reasons:
            risks.extend(f"{label} {reason}" for reason in reasons[:2])

    unique_risks = list(dict.fromkeys(risks))[:5]

    return EvaluationResult(
        pain_point_clarity=public.pain_point_clarity,
        solution_appropriateness=public.solution_appropriateness,
        public_feasibility=public.public_feasibility,
        requirement_coverage=intent.requirement_coverage,
        success_criteria_met=intent.success_criteria_met,
        fidelity_no_bloat=intent.fidelity_no_bloat,
        setup_instructions=readme_scores.setup_instructions,
        documentation_accuracy=readme_scores.documentation_accuracy,
        maintainability=readme_scores.maintainability,
        strengths=review.strengths,
        risks=unique_risks if unique_risks else review.risks,
        final_verdict=review.final_verdict,
    )
