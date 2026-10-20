from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


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
