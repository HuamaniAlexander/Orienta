"""Optional inference from independently evaluated, trusted local artifacts."""

import json
from hashlib import sha256

import joblib

from app.domain.recommendation import CRITERIA, LABELS, approved, features

FIELDS = dict(
    zip(
        CRITERIA,
        (
            "duration_months",
            "modality",
            "location",
            "monthly_cost_pen",
            "requirements",
            "employment",
        ),
    )
)
PREFERENCES = dict(
    zip(
        CRITERIA,
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


class ReviewedRecommendations:
    def __init__(self, directory):
        self.directory = directory

    def analyze(self, left, right, preferences):
        status = dict(
            status="awaiting_reviewed_labels",
            quality_target=0.90,
            quality_approved=False,
            message="Recomendaciones aprendidas pendientes "
            "de revisión y evaluación; las orientaciones actuales se basan en "
            "los datos de las fichas.",
        )
        if not (self.directory / "report.json").exists():
            return status, {}
        try:
            report = json.loads((self.directory / "report.json").read_text(encoding="utf8"))
            if not all(approved(report["criteria"][k]["test"]) for k in CRITERIA):
                return status | dict(status="below_quality_target"), {}
            path = self.directory / "recommendations.joblib"
            if sha256(path.read_bytes()).hexdigest() != report["artifact_sha256"]:
                raise ValueError("Artefacto alterado")
            models = joblib.load(path)
            predictions = {}
            for key, field in FIELDS.items():
                a, b = getattr(left, field), getattr(right, field)
                if a is None or b is None:
                    predictions[key] = "insufficient_data"
                elif preferences.get(PREFERENCES[key]) in (None, ""):
                    predictions[key] = "needs_preference"
                else:
                    predictions[key] = str(
                        models[key].predict(
                            [
                                features(
                                    dict(
                                        criterion=key,
                                        left_value=a,
                                        right_value=b,
                                        preferences=preferences,
                                    )
                                )
                            ]
                        )[0]
                    )
            if any(label not in LABELS for label in predictions.values()):
                raise ValueError("Etiqueta no reconocida")
            return status | dict(
                status="evaluated",
                quality_approved=True,
                message="Predicciones del modelo revisado; confirma sus "
                "condiciones y fuentes antes de decidir.",
            ), predictions
        except (OSError, ValueError, KeyError, EOFError):
            return status | dict(status="unavailable"), {}
