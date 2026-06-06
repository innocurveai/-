from pydantic import BaseModel, Field, field_validator


class PublicSectorScores(BaseModel):
    pain_point_clarity: int = Field(ge=0, le=100)
    solution_appropriateness: int = Field(ge=0, le=100)
    public_feasibility: int = Field(ge=0, le=100)


class IntentScores(BaseModel):
    requirement_coverage: int = Field(ge=0, le=100)
    success_criteria_met: int = Field(ge=0, le=100)
    fidelity_no_bloat: int = Field(ge=0, le=100)


class ReadmeScores(BaseModel):
    setup_instructions: int = Field(ge=0, le=100)
    documentation_accuracy: int = Field(ge=0, le=100)
    maintainability: int = Field(ge=0, le=100)


class ReviewSummary(BaseModel):
    strengths: list[str] = Field(min_length=1)
    risks: list[str] = Field(min_length=1)
    final_verdict: str = Field(min_length=30, max_length=280)

    @field_validator("strengths", "risks")
    @classmethod
    def strip_items(cls, value: list[str]) -> list[str]:
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
