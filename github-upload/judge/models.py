from pydantic import BaseModel, Field, field_validator

# ── 분야 1: 공공기관 적합성 ──
PUBLIC_SECTOR_FIELDS: dict[str, str] = {
    "pain_point_clarity": "페인포인트 명확성",
    "solution_appropriateness": "해결 방향 적절성",
    "public_feasibility": "공공 현장 적용 가능성",
}

# ── 분야 2: 의도 구현도 ──
INTENT_IMPLEMENTATION_FIELDS: dict[str, str] = {
    "requirement_coverage": "핵심 요구사항 구현",
    "success_criteria_met": "성공 기준 충족",
    "fidelity_no_bloat": "의도 충실·과잉 없음",
}

# ── 분야 3: README 품질 ──
README_QUALITY_FIELDS: dict[str, str] = {
    "setup_instructions": "설치·실행 안내",
    "documentation_accuracy": "기획·코드 정합성",
    "maintainability": "유지보수·확장 가이드",
}

DOMAIN_LABELS: dict[str, str] = {
    "public_sector": "공공기관 적합성",
    "intent_implementation": "의도 구현도",
    "readme_quality": "README 품질",
}


class EvaluationResult(BaseModel):
    """3대 심사 분야 × 세부 9항목 평가 결과."""

    # 분야 1 — 기획서 기준 공공기관 적합성
    pain_point_clarity: int = Field(ge=0, le=100)
    solution_appropriateness: int = Field(ge=0, le=100)
    public_feasibility: int = Field(ge=0, le=100)

    # 분야 2 — 기획서 ↔ 실행 코드
    requirement_coverage: int = Field(ge=0, le=100)
    success_criteria_met: int = Field(ge=0, le=100)
    fidelity_no_bloat: int = Field(ge=0, le=100)

    # 분야 3 — README (specs/README_RUBRIC.md 기준)
    setup_instructions: int = Field(ge=0, le=100)
    documentation_accuracy: int = Field(ge=0, le=100)
    maintainability: int = Field(ge=0, le=100)

    strengths: list[str] = Field(min_length=1, description="잘한 점 2~5개")
    risks: list[str] = Field(min_length=1, description="감점 요인 1~5개")
    final_verdict: str = Field(
        min_length=30,
        max_length=280,
        description=(
            "최종 한마디: 정확히 3문장(3줄). "
            "칭찬·격려 중심, 간결한 총평. "
            "읽는 이가 기분 좋게 느낄 따뜻한 톤."
        ),
    )

    @field_validator("strengths", "risks")
    @classmethod
    def strip_non_empty_items(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if item.strip()]
        if not cleaned:
            raise ValueError("목록에는 최소 하나의 항목이 필요합니다.")
        return cleaned

    @field_validator("final_verdict")
    @classmethod
    def strip_verdict(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("최종 한마디는 비어 있을 수 없습니다.")
        return cleaned

    @staticmethod
    def _avg(values: list[int]) -> float:
        return round(sum(values) / len(values), 1)

    @staticmethod
    def _avg_float(values: list[float]) -> float:
        return round(sum(values) / len(values), 1)

    @property
    def public_sector_score(self) -> float:
        return self._avg(
            [
                self.pain_point_clarity,
                self.solution_appropriateness,
                self.public_feasibility,
            ]
        )

    @property
    def intent_implementation_score(self) -> float:
        return self._avg(
            [
                self.requirement_coverage,
                self.success_criteria_met,
                self.fidelity_no_bloat,
            ]
        )

    @property
    def readme_quality_score(self) -> float:
        return self._avg(
            [
                self.setup_instructions,
                self.documentation_accuracy,
                self.maintainability,
            ]
        )

    @property
    def total_score(self) -> float:
        return self._avg_float(
            [
                self.public_sector_score,
                self.intent_implementation_score,
                self.readme_quality_score,
            ]
        )

    def domain_summary_rows(self) -> list[dict[str, object]]:
        return [
            {"분야": DOMAIN_LABELS["public_sector"], "점수": self.public_sector_score},
            {
                "분야": DOMAIN_LABELS["intent_implementation"],
                "점수": self.intent_implementation_score,
            },
            {"분야": DOMAIN_LABELS["readme_quality"], "점수": self.readme_quality_score},
            {"분야": "종합", "점수": self.total_score},
        ]

    def detail_score_rows(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []

        for field, label in PUBLIC_SECTOR_FIELDS.items():
            rows.append(
                {
                    "분야": DOMAIN_LABELS["public_sector"],
                    "세부 항목": label,
                    "점수": getattr(self, field),
                }
            )
        for field, label in INTENT_IMPLEMENTATION_FIELDS.items():
            rows.append(
                {
                    "분야": DOMAIN_LABELS["intent_implementation"],
                    "세부 항목": label,
                    "점수": getattr(self, field),
                }
            )
        for field, label in README_QUALITY_FIELDS.items():
            rows.append(
                {
                    "분야": DOMAIN_LABELS["readme_quality"],
                    "세부 항목": label,
                    "점수": getattr(self, field),
                }
            )
        return rows
