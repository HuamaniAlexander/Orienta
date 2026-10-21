import json
from hashlib import sha256
from pathlib import Path
from threading import Lock

import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from app.adapters.output.caracteristicas_ia import caracteristicas, firma
from app.domain.carrera import Carrera
from app.ports.motor_analisis import AnalisisNoDisponible


class AnalisisEntrenado:
    """Carga un artefacto local una vez y verifica su integridad antes de inferir."""

    def __init__(self, directorio: Path):
        self.directorio = directorio
        self._artefacto = None
        self._informe = None
        self._bloqueo = Lock()

    def _cargar(self):
        with self._bloqueo:
            if self._artefacto is not None:
                return
            try:
                informe = json.loads(
                    (self.directorio / "metricas.json").read_text(encoding="utf-8")
                )
                ruta = self.directorio / "modelo.joblib"
                if sha256(ruta.read_bytes()).hexdigest() != informe["artifact_sha256"]:
                    raise ValueError("Modelo alterado")
                artefacto = joblib.load(ruta)
                self._artefacto, self._informe = artefacto, informe
            except (OSError, ValueError, KeyError, EOFError) as error:
                raise AnalisisNoDisponible(
                    "El análisis no está disponible. "
                    "Conserva la comparación e inténtalo nuevamente."
                ) from error

    def analizar(self, izquierda: Carrera, derecha: Carrera):
        self._cargar()
        informe, artefacto = self._informe, self._artefacto
        for c in (izquierda, derecha):
            if (
                c.id not in informe["metadata"]
                or firma(c) != informe["metadata"][c.id]["signature"]
            ):
                raise AnalisisNoDisponible(
                    "Estas ofertas requieren actualizar el modelo antes de analizarlas."
                )
        try:
            etiqueta = int(
                artefacto["classifier"].predict(
                    pd.DataFrame([caracteristicas(izquierda, derecha)])
                )[0]
            )
            real = int(
                informe["metadata"][izquierda.id]["area"] != informe["metadata"][derecha.id]["area"]
            )
            identificadores = artefacto["ids"]
            # La similitud de contenido es independiente del clasificador supervisado de áreas.
            indices = [identificadores.index(izquierda.id), identificadores.index(derecha.id)]
            consulta = artefacto["content_matrix"][indices].mean(axis=0)
            import numpy as np

            puntuaciones = cosine_similarity(np.asarray(consulta), artefacto["content_matrix"])[0]
            ordenados = sorted(
                range(len(identificadores)), key=lambda i: (-puntuaciones[i], identificadores[i])
            )
            relacionadas = [
                identificadores[i]
                for i in ordenados
                if identificadores[i] not in (izquierda.id, derecha.id) and puntuaciones[i] > 0
            ]
        except (ValueError, KeyError, IndexError) as error:
            raise AnalisisNoDisponible(
                "No pudimos analizar estas alternativas. Inténtalo nuevamente."
            ) from error
        seleccionado = informe["models"][informe["selected_model"]]
        return {
            "quality_target": informe.get("quality_target", 0.90),
            "quality_approved": informe.get("quality_approved", False),
            "model_evaluations": [
                dict(
                    name=nombre,
                    **{
                        clave: valores[clave]
                        for clave in ("accuracy", "precision_macro", "recall_macro", "f1_macro")
                    },
                    validation_distance_to_ideal=valores.get("validation_distance_to_ideal"),
                )
                for nombre, valores in informe["models"].items()
            ],
            "prediction": "Áreas distintas" if etiqueta else "Misma área",
            "catalog_contrast": "Áreas distintas" if real else "Misma área",
            "areas": [informe["metadata"][c.id]["area"] for c in (izquierda, derecha)],
            "area_sources": [informe["metadata"][c.id]["source"] for c in (izquierda, derecha)],
            "agrees_with_catalog": etiqueta == real,
            "model_name": informe["selected_model"],
            "model_version": informe["version"],
            "metrics": {
                k: seleccionado[k]
                for k in ["accuracy", "precision_macro", "recall_macro", "f1_macro"]
            },
            "baseline_accuracy": informe["baseline"]["accuracy"],
            "training_pairs": informe["training_pairs"],
            "test_pairs": informe["test_pairs"],
            "limitations": informe["limitations"],
            "next_steps": [
                "Consulta la malla curricular y los requisitos de ambas instituciones.",
                "Confirma costos, becas y gastos adicionales antes de estimar tu presupuesto.",
                "Revisa horarios, sede y modalidad según tu disponibilidad.",
            ],
            "related_ids": relacionadas,
        }
