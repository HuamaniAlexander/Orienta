from dataclasses import dataclass
from decimal import Decimal

from app.domain.carrera import Carrera


class ComparacionInvalida(Exception):
    pass


@dataclass(frozen=True)
class Comparacion:
    izquierda: Carrera
    derecha: Carrera
    diferencia_duracion_meses: int | None
    diferencia_costo_mensual_soles: Decimal | None


def comparar(izquierda: Carrera, derecha: Carrera) -> Comparacion:
    if izquierda.id == derecha.id or izquierda.identidad == derecha.identidad:
        raise ComparacionInvalida("Selecciona dos alternativas diferentes")
    duracion = (
        None
        if izquierda.duracion_meses is None or derecha.duracion_meses is None
        else (derecha.duracion_meses - izquierda.duracion_meses)
    )
    costo = (
        None
        if izquierda.costo_mensual_soles is None or derecha.costo_mensual_soles is None
        else (derecha.costo_mensual_soles - izquierda.costo_mensual_soles)
    )
    return Comparacion(izquierda, derecha, duracion, costo)
