from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    field: str
    reference: str | None
    status: str


class CareerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    institution: str
    training_type: str | None
    modality: str | None
    location: str | None
    duration_months: int | None
    monthly_cost_pen: Decimal | None
    requirements: str | None
    employment: str | None
    reviewed_on: date | None
    sources: list[SourceResponse]


class CatalogResponse(BaseModel):
    items: list[CareerResponse]
    total: int
    pagina: int
    limite: int
    data_mode: str


class ComparisonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    career_ids: list[str] = Field(min_length=2, max_length=2)


class ComparisonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    left: CareerResponse
    right: CareerResponse
    duration_difference_months: int | None
    monthly_cost_difference_pen: Decimal | None


class RecommendationPreferences(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    budget_pen: float | None = Field(default=None, ge=0)
    max_duration_months: int | None = Field(default=None, ge=1, le=240)
    modality: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=200)
    employment_interests: str | None = Field(default=None, max_length=500)
    requirements_met: str | None = Field(default=None, max_length=500)


class AnalysisRequest(ComparisonRequest):
    preferences: RecommendationPreferences = Field(default_factory=RecommendationPreferences)


class CriterionAnalysisResponse(BaseModel):
    learned_label: str | None = None
    reason: str
    left_label: str
    right_label: str
    key: str
    label: str
    left_value: str
    right_value: str
    relationship: str
    explanation: str
    recommendation: str
    caveats: list[str]


class AnalysisResponse(BaseModel):
    recommendation_training: dict
    criteria_analysis: list[CriterionAnalysisResponse]
    explanation_kind: str
    quality_target: float
    quality_approved: bool
    model_evaluations: list[dict[str, str | float | None]]
    prediction: str
    catalog_contrast: str
    areas: list[str]
    area_sources: list[str | None]
    agrees_with_catalog: bool
    model_name: str
    model_version: str
    metrics: dict[str, float]
    baseline_accuracy: float
    training_pairs: int
    test_pairs: int
    limitations: list[str]
    next_steps: list[str]
    recommendations: list[CareerResponse]
