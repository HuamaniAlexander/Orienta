"""Ofertas académicas sin dependencias de frameworks."""

import unicodedata
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


def normalizar(valor: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", valor.casefold()) if not unicodedata.combining(c)
    ).strip()


@dataclass(frozen=True)
class Fuente:
    campo: str
    referencia: str | None
    estado: str


@dataclass(frozen=True)
class Carrera:
    id: str
    nombre: str
    institucion: str
    tipo_formacion: str | None
    modalidad: str | None
    ubicacion: str | None
    duracion_meses: int | None
    costo_mensual_soles: Decimal | None
    requisitos: str | None
    campo_laboral: str | None
    fecha_revision: date | None
    fuentes: tuple[Fuente, ...]
    activa: bool = True
    detalles: dict = field(default_factory=dict)

    def __post_init__(self):
        if not all(v.strip() for v in (self.id, self.nombre, self.institucion)):
            raise ValueError("Código, carrera e institución son obligatorios")
        if self.duracion_meses is not None and self.duracion_meses <= 0:
            raise ValueError("La duración debe ser positiva")
        if self.costo_mensual_soles is not None and (
            not self.costo_mensual_soles.is_finite() or self.costo_mensual_soles < 0
        ):
            raise ValueError("El costo debe ser finito y no negativo")

    @property
    def identidad(self) -> tuple[str, ...]:
        return tuple(
            normalizar(v or "")
            for v in (self.nombre, self.institucion, self.ubicacion, self.modalidad)
        )
