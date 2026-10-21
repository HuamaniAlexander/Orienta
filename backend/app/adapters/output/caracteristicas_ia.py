"""Entradas simétricas sin nombres, áreas, grupos ni identificadores como predictores."""

import json
from hashlib import sha256

from app.domain.carrera import Carrera

NUMERICAS = ["cost_difference", "cost_mean", "duration_difference", "duration_mean"]
CATEGORICAS = ["institution_a", "institution_b", "modality_a", "modality_b"]


def firma(c: Carrera) -> str:
    valores = [
        c.id,
        c.nombre,
        c.institucion,
        c.modalidad,
        c.ubicacion,
        c.duracion_meses,
        format(c.costo_mensual_soles, ".2f") if c.costo_mensual_soles is not None else None,
        c.campo_laboral,
        c.requisitos,
    ]
    return sha256(json.dumps(valores, ensure_ascii=False).encode()).hexdigest()


def caracteristicas(izquierda: Carrera, derecha: Carrera) -> dict:
    a, b = sorted([izquierda, derecha], key=lambda c: c.id)
    fila = {}
    for prefijo, valores in [
        ("cost", [a.costo_mensual_soles, b.costo_mensual_soles]),
        ("duration", [a.duracion_meses, b.duracion_meses]),
    ]:
        if any(v is None for v in valores):
            fila[prefijo + "_difference"] = float("nan")
            fila[prefijo + "_mean"] = float("nan")
        else:
            fila[prefijo + "_difference"] = abs(float(valores[0]) - float(valores[1]))
            fila[prefijo + "_mean"] = (float(valores[0]) + float(valores[1])) / 2
    for sufijo, c in [("a", a), ("b", b)]:
        fila["institution_" + sufijo] = c.institucion
        fila["modality_" + sufijo] = c.modalidad or "Sin modalidad"
    return fila
