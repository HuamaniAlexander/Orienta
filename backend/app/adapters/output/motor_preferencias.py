"""Inferencia local con contribuciones exactas de regresión logística."""

import json
from hashlib import sha256
from pathlib import Path

import joblib
import numpy as np

from app.domain.perfil_vocacional import NOMBRES_FACTORES, VERSION_CARACTERISTICAS


class MotorPreferenciasLocal:
    def __init__(self, directorio: Path):
        self.directorio = directorio

    def predecir(self, caracteristicas):
        ausente = {
            "estado": "sin_modelo",
            "explicacion": (
                "Aún no existe un modelo de preferencias entrenado y evaluado con "
                "elecciones reales autorizadas. Tus respuestas no se sustituyen "
                "por una recomendación simulada."
            ),
        }
        try:
            informe = json.loads((self.directorio / "informe.json").read_text(encoding="utf-8"))
            ruta = self.directorio / "preferencias.joblib"
            if (
                informe["version_caracteristicas"] != VERSION_CARACTERISTICAS
                or not informe["habilitado"]
            ):
                return ausente | {
                    "estado": "modelo_no_aprobado",
                    "explicacion": (
                        "El modelo no supera los criterios de evaluación independiente; "
                        "puedes revisar las fichas y modificar tus respuestas."
                    ),
                }
            if sha256(ruta.read_bytes()).hexdigest() != informe["sha256"]:
                raise ValueError("Integridad incorrecta")
            modelo = joblib.load(ruta)
            vector = modelo.named_steps["vectorizador"].transform([caracteristicas])
            escalado = modelo.named_steps["escalador"].transform(vector)
            clasificador = modelo.named_steps["clasificador"]
            if clasificador.fit_intercept or list(clasificador.classes_) != [0, 1]:
                raise ValueError("Modelo incompatible")
            valores = np.asarray(escalado[0]) * clasificador.coef_[0]
            nombres = modelo.named_steps["vectorizador"].get_feature_names_out()
            factores = [
                {
                    "factor": str(nombre),
                    "descripcion": NOMBRES_FACTORES[str(nombre)],
                    "valor": float(caracteristicas[str(nombre)]),
                    "contribucion": float(valor),
                }
                for nombre, valor in zip(nombres, valores, strict=True)
            ]
            margen = float(modelo.decision_function([caracteristicas])[0])
            if (
                not np.isfinite(margen)
                or abs(sum(f["contribucion"] for f in factores) - margen) > 1e-8
            ):
                raise ValueError("No se pudo explicar el margen")
            return {
                "estado": "disponible",
                "margen": margen,
                "umbral_similitud": 0.2,
                "contribuciones": sorted(factores, key=lambda f: -abs(f["contribucion"])),
                "modelo": {
                    "version": informe["version"],
                    "algoritmo": "Regresión logística de preferencias entre pares",
                    "evaluacion": informe["prueba"],
                    "significado_margen": (
                        "Log-odds de preferencia relativa por la primera oferta en orden "
                        "canónico; no es éxito profesional."
                    ),
                },
            }
        except FileNotFoundError:
            return ausente
        except (OSError, ValueError, KeyError, EOFError, TypeError, AttributeError):
            return ausente | {
                "estado": "modelo_no_disponible",
                "explicacion": (
                    "No se pudo verificar el modelo local. Puedes reintentar o "
                    "continuar comparando las fichas."
                ),
            }
