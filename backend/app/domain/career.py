"""Academic offers; no framework dependencies."""

import unicodedata
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


def normalize(value: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", value.casefold()) if not unicodedata.combining(c)
    ).strip()


@dataclass(frozen=True)
class Source:
    field: str
    reference: str | None
    status: str


@dataclass(frozen=True)
class Career:
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
    sources: tuple[Source, ...]
    active: bool = True

    def __post_init__(self):
        if not all(v.strip() for v in (self.id, self.name, self.institution)):
            raise ValueError("Código, carrera e institución son obligatorios")
        if self.duration_months is not None and self.duration_months <= 0:
            raise ValueError("La duración debe ser positiva")
        if self.monthly_cost_pen is not None and (
            not self.monthly_cost_pen.is_finite() or self.monthly_cost_pen < 0
        ):
            raise ValueError("El costo debe ser finito y no negativo")

    @property
    def identity(self) -> tuple[str, ...]:
        return tuple(
            normalize(v or "") for v in (self.name, self.institution, self.location, self.modality)
        )
