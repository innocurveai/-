"""메타 채점: specs/PLAN.md + README + 핵심 코드."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from judge.evaluator import EvaluationError, build_user_message, run_evaluation, validate_inputs

CODE_FILES = [
    ROOT / "app.py",
    ROOT / "judge" / "models.py",
    ROOT / "judge" / "evaluator.py",
    ROOT / "judge" / "formatter.py",
]


def load_plan() -> str:
    return (ROOT / "specs" / "PLAN.md").read_text(encoding="utf-8")


def load_readme() -> str:
    return (ROOT / "README.md").read_text(encoding="utf-8")


def load_code() -> str:
    parts: list[str] = []
    for path in CODE_FILES:
        if path.exists():
            parts.append(f"# --- {path.name} ---\n{path.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def main() -> int:
    plan = load_plan()
    readme = load_readme()
    code = load_code()
    validate_inputs(plan, readme, code)
    message = build_user_message(plan, readme, code)

    print("META_INPUT_OK")
    print(
        f"plan_chars={len(plan)} readme_chars={len(readme)} "
        f"code_chars={len(code)} user_msg_chars={len(message)}"
    )

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-your"):
        print("META_EVAL_SKIPPED_NO_API_KEY")
        return 0

    try:
        result = run_evaluation(plan, readme, code, api_key=api_key)
    except EvaluationError as exc:
        print(f"META_EVAL_FAILED: {exc}", file=sys.stderr)
        return 1

    print(f"META_EVAL_SCORE={result.total_score}")
    print(f"public_sector={result.public_sector_score}")
    print(f"intent={result.intent_implementation_score}")
    print(f"readme={result.readme_quality_score}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
