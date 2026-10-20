"""Inferencia opcional con artefactos locales evaluados de forma independiente."""

import json
from hashlib import sha256

import joblib

from app.domain.recomendacion import CRITERIOS, ETIQUETAS, caracteristicas, cumple_umbral

CAMPOS = dict(
    zip(
        CRITERIOS,
        (
            "duracion_meses",
            "modalidad",
            "ubicacion",
            "costo_mensual_soles",
            "requisitos",
            "campo_laboral",
        ),
    )
)
PREFERENCIAS = dict(
    zip(
        CRITERIOS,
        (
            "max_duration_months",
            "modality",
            "location",
            "budget_pen",
            "requirements_met",
            "employment_interests",
        ),
    )
)


class RecomendacionesRevisadas:
    def __init__(self, directorio):
        self.directorio = directorio

    def analizar(self, izquierda, derecha, preferencias):
        estado = dict(
            status="awaiting_reviewed_labels",
            quality_target=0.90,
            quality_approved=False,
            message="Recomendaciones aprendidas pendientes "
            "de revisión y evaluación; las orientaciones actuales se basan en "
            "los datos de las fichas.",
        )
        if not (self.directorio / "informe.json").exists():
            return estado, {}
        try:
            informe = json.loads((self.directorio / "informe.json").read_text(encoding="utf8"))
            if not all(cumple_umbral(informe["criteria"][k]["test"]) for k in CRITERIOS):
                return estado | dict(status="below_quality_target"), {}
            ruta = self.directorio / "recomendaciones.joblib"
            if sha256(ruta.read_bytes()).hexdigest() != informe["artifact_sha256"]:
                raise ValueError("Artefacto alterado")
            modelos = joblib.load(ruta)
            predicciones = {}
            for clave, campo in CAMPOS.items():
                a, b = getattr(izquierda, campo), getattr(derecha, campo)
                if a is None or b is None:
                    predicciones[clave] = "insufficient_data"
                elif preferencias.get(PREFERENCIAS[clave]) in (None, ""):
                    predicciones[clave] = "needs_preference"
                else:
                    predicciones[clave] = str(
                        modelos[clave].predict(
                            [
                                caracteristicas(
                                    dict(
                                        criterion=clave,
                                        left_value=a,
                                        right_value=b,
                                        preferences=preferencias,
                                    )
                                )
                            ]
                        )[0]
                    )
            if any(etiqueta not in ETIQUETAS for etiqueta in predicciones.values()):
                raise ValueError("Etiqueta no reconocida")
            return estado | dict(
                status="evaluated",
                quality_approved=True,
                message="Predicciones del modelo revisado; confirma sus "
                "condiciones y fuentes antes de decidir.",
            ), predicciones
        except (OSError, ValueError, KeyError, EOFError):
            return estado | dict(status="unavailable"), {}
