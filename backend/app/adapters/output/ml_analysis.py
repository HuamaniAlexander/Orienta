import json
from hashlib import sha256
from pathlib import Path
from threading import Lock

import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from app.adapters.output.ml_features import features, signature
from app.domain.career import Career
from app.ports.analysis import AnalysisUnavailable


class TrainedAnalysis:
    """Loads a trusted, hash-checked local artifact once. No training or remote requests."""

    def __init__(self, directory: Path):
        self.directory = directory
        self._artifact = None
        self._report = None
        self._lock = Lock()

    def _load(self):
        with self._lock:
            if self._artifact is not None:
                return
            try:
                report = json.loads((self.directory / "metrics.json").read_text(encoding="utf-8"))
                path = self.directory / "model.joblib"
                if sha256(path.read_bytes()).hexdigest() != report["artifact_sha256"]:
                    raise ValueError("Modelo alterado")
                artifact = joblib.load(path)
                self._artifact, self._report = artifact, report
            except (OSError, ValueError, KeyError, EOFError) as error:
                raise AnalysisUnavailable(
                    "El análisis no está disponible. "
                    "Conserva la comparación e inténtalo nuevamente."
                ) from error

    def analyze(self, left: Career, right: Career):
        self._load()
        report, artifact = self._report, self._artifact
        for c in (left, right):
            if (
                c.id not in report["metadata"]
                or signature(c) != report["metadata"][c.id]["signature"]
            ):
                raise AnalysisUnavailable(
                    "Estas ofertas requieren actualizar el modelo antes de analizarlas."
                )
        try:
            label = int(artifact["classifier"].predict(pd.DataFrame([features(left, right)]))[0])
            actual = int(
                report["metadata"][left.id]["area"] != report["metadata"][right.id]["area"]
            )
            ids = artifact["ids"]
            # Content similarity is unsupervised and separate from the contrast classifier.
            indices = [ids.index(left.id), ids.index(right.id)]
            query = artifact["content_matrix"][indices].mean(axis=0)
            import numpy as np

            scores = cosine_similarity(np.asarray(query), artifact["content_matrix"])[0]
            ranked = sorted(range(len(ids)), key=lambda i: (-scores[i], ids[i]))
            related = [
                ids[i] for i in ranked if ids[i] not in (left.id, right.id) and scores[i] > 0
            ]
        except (ValueError, KeyError, IndexError) as error:
            raise AnalysisUnavailable(
                "No pudimos analizar estas alternativas. Inténtalo nuevamente."
            ) from error
        selected = report["models"][report["selected_model"]]
        return {
            "prediction": "Áreas distintas" if label else "Misma área",
            "catalog_contrast": "Áreas distintas" if actual else "Misma área",
            "areas": [report["metadata"][c.id]["area"] for c in (left, right)],
            "area_sources": [report["metadata"][c.id]["source"] for c in (left, right)],
            "agrees_with_catalog": label == actual,
            "model_name": report["selected_model"],
            "model_version": report["version"],
            "metrics": {
                k: selected[k] for k in ["accuracy", "precision_macro", "recall_macro", "f1_macro"]
            },
            "baseline_accuracy": report["baseline"]["accuracy"],
            "training_pairs": report["training_pairs"],
            "test_pairs": report["test_pairs"],
            "limitations": report["limitations"],
            "next_steps": [
                "Consulta la malla curricular y los requisitos de ambas instituciones.",
                "Confirma costos, becas y gastos adicionales antes de estimar tu presupuesto.",
                "Revisa horarios, sede y modalidad según tu disponibilidad.",
            ],
            "related_ids": related,
        }
