"""Validated reader for the supplied PoC workbook. Never interprets ML codes."""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from openpyxl import load_workbook

from app.domain.career import Career, Source

REQUIRED = {
    "id_carrera",
    "carrera",
    "institucion",
    "duracion_meses",
    "modalidad",
    "ubicacion",
    "costo_mensual_soles",
    "requisitos",
    "campo_laboral",
    "estado_costo",
    "estado_modalidad",
    "fuente_carrera",
    "fuente_costo",
    "fuente_requisitos",
    "fecha_revision",
    "fuente_duracion",
}
UNIVERSITIES = {"UTP", "UNMSM", "UNI", "UPCH"}


def text(value):
    return str(value).strip() if value is not None and str(value).strip() else None


def read_careers(path: Path) -> list[Career]:
    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        if "Carreras" not in wb.sheetnames:
            raise ValueError("Falta la hoja Carreras")
        rows = iter(wb["Carreras"].values)
        headers = next(rows, ())
        if not REQUIRED.issubset(headers) or len(headers) != len(set(headers)):
            raise ValueError("Columnas obligatorias ausentes o duplicadas")
        result, ids, identities = [], set(), set()
        for number, values in enumerate(rows, 2):
            if all(v is None for v in values):
                continue
            row = dict(zip(headers, values))
            try:

                def numeric(key):
                    value = text(row[key])
                    return Decimal(value) if value is not None else None

                duration = numeric("duracion_meses")
                if duration is not None and (
                    not duration.is_finite() or duration != duration.to_integral_value()
                ):
                    raise ValueError("Duración en meses enteros requerida")
                reviewed = row["fecha_revision"]
                if isinstance(reviewed, datetime):
                    reviewed = reviewed.date()
                elif reviewed is not None and not isinstance(reviewed, date):
                    reviewed = date.fromisoformat(str(reviewed))
                institution = text(row["institucion"]) or ""
                sources = tuple(
                    Source(
                        field,
                        text(row.get(reference)),
                        (text(row.get(status)) or "Sin estado registrado")
                        if status
                        else "Según PoC; sin verificar",
                    )
                    for field, reference, status in [
                        ("Carrera", "fuente_carrera", None),
                        ("Duración", "fuente_duracion", None),
                        ("Modalidad", "fuente_carrera", "estado_modalidad"),
                        ("Costo", "fuente_costo", "estado_costo"),
                        ("Requisitos", "fuente_requisitos", None),
                        ("Campo laboral", "fuente_campo_laboral", None),
                    ]
                )
                career = Career(
                    id=text(row["id_carrera"]) or "",
                    name=text(row["carrera"]) or "",
                    institution=institution,
                    training_type="Universitaria" if institution in UNIVERSITIES else None,
                    modality=text(row["modalidad"]),
                    location=text(row["ubicacion"]),
                    duration_months=int(duration) if duration is not None else None,
                    monthly_cost_pen=numeric("costo_mensual_soles"),
                    requirements=text(row["requisitos"]),
                    employment=text(row["campo_laboral"]),
                    reviewed_on=reviewed,
                    sources=sources,
                )
                if career.id in ids or career.identity in identities:
                    raise ValueError(
                        "Oferta duplicada por código o carrera/institución/sede/modalidad"
                    )
                ids.add(career.id)
                identities.add(career.identity)
                result.append(career)
            except (ValueError, InvalidOperation, TypeError) as error:
                raise ValueError(f"Fila {number}: {error}") from error
        if not result:
            raise ValueError("El libro no contiene ofertas")
        return result
    finally:
        wb.close()
