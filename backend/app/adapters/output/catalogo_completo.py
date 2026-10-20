"""Lectura validada del catálogo entregado, sin descartar ofertas ni procedencia."""

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from app.domain.carrera import Carrera, Fuente


def leer_catalogo_completo(ruta: Path) -> list[Carrera]:
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    instituciones = {fila["id"]: fila for fila in datos["instituciones"]}
    conceptos = {fila["id"]: fila for fila in datos["carreras"]}
    programas = datos["programas"]
    if len({p["id"] for p in programas}) != len(programas):
        raise ValueError("El catálogo contiene identificadores repetidos")
    if set(instituciones) != {p["institucion_id"] for p in programas}:
        raise ValueError("Las instituciones no coinciden con las ofertas")
    if set(conceptos) != {p["carrera_id"] for p in programas}:
        raise ValueError("Las carreras no coinciden con las ofertas")
    carreras = []
    campos = {
        "Duración": "duracion",
        "Modalidad": "modalidad",
        "Ubicación": "sede",
        "Costo": "matricula_y_pensiones",
        "Requisitos": "requisitos_y_titulo",
        "Campo laboral": "actividades_y_perfil",
    }
    for programa in programas:
        institucion = instituciones[programa["institucion_id"]]
        referencias = programa["fuentes"]
        procedencia = programa["procedencia_comparacion"]
        fuentes = tuple(
            Fuente(
                campo,
                referencias[0] if referencias else None,
                "Estimación del catálogo; confirmar con la institución"
                if procedencia[clave] == "estimacion"
                else "Síntesis académica del catálogo"
                if procedencia[clave] == "sintesis_academica"
                else "Sede modelada; confirmar disponibilidad"
                if programa.get("sede_modelada_por_catalogo_institucional") and clave == "sede"
                else "Catálogo institucional citado; confirmar vigencia",
            )
            for campo, clave in campos.items()
        )
        carreras.append(
            Carrera(
                id=programa["id"],
                nombre=programa["nombre"],
                institucion=institucion["nombre"],
                tipo_formacion="Universitaria"
                if programa["nivel_educativo"] == "universitario"
                else "Técnica",
                modalidad=programa["modalidad"].capitalize(),
                ubicacion=programa["distrito"],
                duracion_meses=programa["duracion_meses"],
                costo_mensual_soles=Decimal(str(programa["costos"]["pension_mensual_soles"])),
                requisitos="; ".join(programa["requisitos_admision"]),
                campo_laboral="; ".join(programa["campo_laboral"]),
                fecha_revision=date.fromisoformat(datos["metadatos"]["fecha_referencia"]),
                fuentes=fuentes,
                detalles=programa | {"sitio_web": institucion["sitio_web"]},
            )
        )
    return carreras
