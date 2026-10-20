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
