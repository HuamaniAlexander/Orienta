import json
from dataclasses import asdict
from decimal import Decimal
from hashlib import sha256

from app.application.comparar_carreras import CompararCarreras
from app.domain.cuestionario import VERSION_CUESTIONARIO, generar_cuestionario, validar_respuestas
from app.domain.perfil_vocacional import (
    VERSION_CARACTERISTICAS,
    extraer_caracteristicas,
    hay_informacion,
)


def huella_programas(carreras):
    return sha256(
        json.dumps(
            [asdict(c) for c in sorted(carreras, key=lambda c: c.id)],
            sort_keys=True,
            default=lambda valor: (
                format(valor.normalize(), "f") if isinstance(valor, Decimal) else str(valor)
            ),
            ensure_ascii=False,
        ).encode()
    ).hexdigest()


class RecomendarPreferencia:
    def __init__(self, catalogo, motor, registro=None):
        self.catalogo, self.motor, self.registro = catalogo, motor, registro

    def preparar(self, ids):
        comparacion = CompararCarreras(self.catalogo).ejecutar(ids)
        return comparacion, generar_cuestionario(comparacion.izquierda, comparacion.derecha)

    def ejecutar(self, ids, respuestas, preferencias, version, captura=None):
        comparacion, cuestionario = self.preparar(ids)
        if version != VERSION_CUESTIONARIO:
            raise ValueError("El cuestionario cambió; vuelve a abrirlo")
        validar_respuestas(cuestionario, respuestas, preferencias)
        a, b = sorted((comparacion.izquierda, comparacion.derecha), key=lambda c: c.id)
        caracteristicas = extraer_caracteristicas(a, b, respuestas, preferencias)
        identificador = None
        if captura:
            if captura["eleccion"] not in {a.id, b.id, "ambas", "ninguna", "incierto"}:
                raise ValueError("La elección independiente no corresponde a las ofertas")
            if not self.registro:
                raise ValueError("La captura no está disponible en este modo")
            # Registrar antes de ejecutar cualquier inferencia; elección fuera de predictores.
            identificador = self.registro.guardar(
                {
                    "id_registro": captura["id_registro"],
                    "origen_eleccion": "previa_inferencia",
                    "id_participante": captura["id_participante"],
                    "eleccion": captura["eleccion"],
                    "consentimiento": captura["consentimiento"],
                    "mayor_edad": captura["mayor_edad"],
                    "version_cuestionario": version,
                    "version_caracteristicas": VERSION_CARACTERISTICAS,
                    "programas": [a.id, b.id],
                    "huella_programas": huella_programas([a, b]),
                    "respuestas": respuestas,
                    "preferencias": preferencias,
                    "caracteristicas": caracteristicas,
                    "instantaneas": [asdict(a), asdict(b)],
                }
            )
        base = {
            "programas": cuestionario["programas"],
            "version_cuestionario": version,
            "id_registro": identificador,
            "recomendada": None,
            "factores": [],
            "factores_contrarios": [],
            "modelo": None,
            "aviso": cuestionario["aviso"],
            "incertidumbres": [
                "No estar seguro se trata como información faltante, no como desinterés."
            ]
            if "incierto" in respuestas.values()
            else [],
        }
        if all(respuestas[p] == "ninguna" for p in ("p7", "p8", "p9")):
            return base | {
                "estado": "sin_interes",
                "explicacion": (
                    "Indicaste que ninguna propuesta te interesa. Explora otras "
                    "carreras antes de priorizar una de estas dos."
                ),
            }
        if not hay_informacion(respuestas, preferencias):
            return base | {
                "estado": "informacion_insuficiente",
                "explicacion": (
                    "Todavía no hay preferencias suficientes para estimar afinidad. "
                    "Puedes modificar tus respuestas."
                ),
            }
        if respuestas["p10"] == "empleo":
            base["incertidumbres"].append(
                "El catálogo no incluye empleabilidad observada para "
                "estimar oportunidades laborales."
            )
        prediccion = self.motor.predecir(caracteristicas)
        if prediccion["estado"] != "disponible":
            return base | prediccion
        puntuacion = prediccion["margen"]
        similares = abs(puntuacion) < prediccion["umbral_similitud"]
        elegida, otra = (a, b) if puntuacion > 0 else (b, a)
        signo = 1 if puntuacion > 0 else -1
        favor = [f for f in prediccion["contribuciones"] if f["contribucion"] * signo > 0]
        contra = [f for f in prediccion["contribuciones"] if f["contribucion"] * signo < 0]
        return base | {
            "estado": "afinidad_similar" if similares else "recomendacion",
            "recomendada": None if similares else elegida.id,
            "modelo": prediccion["modelo"],
            "factores": favor,
            "factores_contrarios": contra,
            "margen": puntuacion,
            "explicacion": "Las preferencias aportadas no distinguen claramente ambas opciones."
            if similares
            else (
                f"{elegida.nombre} · {elegida.institucion} "
                "presenta mayor afinidad relativa en este modelo. "
            )
            + ("Influyen " + ", ".join(f["descripcion"] for f in favor[:3]) + ". " if favor else "")
            + (
                f"{otra.nombre} · {otra.institucion} también se ve favorecida por "
                + ", ".join(f["descripcion"] for f in contra[:2])
                + "."
                if contra
                else "Revisa además las condiciones de ambas fichas."
            ),
            "incertidumbres": base["incertidumbres"]
            + ["Los costos y parte de las condiciones académicas del catálogo son estimaciones."],
        }
