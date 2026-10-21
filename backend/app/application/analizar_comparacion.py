from app.application.catalogo import CarreraNoEncontrada, Catalogo
from app.application.comparar_carreras import CompararCarreras
from app.domain.analisis_criterios import analizar_criterios
from app.ports.motor_analisis import AnalisisNoDisponible, MotorAnalisis
from app.ports.motor_recomendaciones import MotorRecomendaciones


class AnalizarComparacion:
    def __init__(
        self,
        catalogo: Catalogo,
        servicio: MotorAnalisis,
        recomendador: MotorRecomendaciones | None = None,
    ):
        self.catalogo, self.servicio = catalogo, servicio
        self.recomendador = recomendador

    def ejecutar(self, identificadores: list[str], preferencias=None):
        comparacion = CompararCarreras(self.catalogo).ejecutar(identificadores)
        try:
            resultado = self.servicio.analizar(comparacion.izquierda, comparacion.derecha)
        except AnalisisNoDisponible:
            # El clasificador histórico no cubre ofertas nuevas. No inventar inferencias
            # ni impedir el contraste de datos y las orientaciones de los seis criterios.
            if not all(c.detalles for c in (comparacion.izquierda, comparacion.derecha)):
                raise
            areas = [
                c.detalles.get("area_conocimiento", "Sin área")
                for c in (comparacion.izquierda, comparacion.derecha)
            ]
            resultado = {
                "quality_target": 0.90,
                "quality_approved": False,
                "model_evaluations": [],
                "prediction": "Sin inferencia para estas ofertas",
                "catalog_contrast": "Misma área" if areas[0] == areas[1] else "Áreas distintas",
                "areas": areas,
                "area_sources": [None, None],
                "agrees_with_catalog": False,
                "model_name": "Pendiente de evaluación para el catálogo ampliado",
                "model_version": "sin-evaluacion",
                "metrics": {},
                "baseline_accuracy": 0,
                "training_pairs": 0,
                "test_pairs": 0,
                "limitations": [
                    "El modelo histórico no fue entrenado con estas ofertas. "
                    "Las orientaciones siguientes son un contraste estructurado."
                ],
                "related_ids": [],
            }
        relacionadas = []
        for id in resultado.pop("related_ids"):
            if id in identificadores:
                continue
            try:
                relacionadas.append(self.catalogo.detalle(id))
                if len(relacionadas) == 3:
                    break
            except CarreraNoEncontrada:
                continue
        criterios = analizar_criterios(comparacion.izquierda, comparacion.derecha)
        estado = {
            "status": "awaiting_reviewed_labels",
            "quality_target": 0.90,
            "quality_approved": False,
            "message": "Recomendaciones aprendidas pendientes de revisión y evaluación; "
            "las orientaciones actuales se basan en los datos de las fichas.",
        }
        if self.recomendador:
            estado, predicciones = self.recomendador.analizar(
                comparacion.izquierda, comparacion.derecha, preferencias or {}
            )
            for elemento in criterios:
                etiqueta = predicciones.get(elemento["clave"])
                elemento["etiqueta_aprendida"] = etiqueta
                if etiqueta:
                    elemento["recomendacion"] = (
                        {
                            "favor_left": (
                                f"Según tus preferencias: {elemento['etiqueta_izquierda']}."
                            ),
                            "favor_right": (
                                f"Según tus preferencias: {elemento['etiqueta_derecha']}."
                            ),
                            "equivalent": "El modelo no identifica una ventaja en este criterio.",
                            "needs_preference": "Indica la preferencia que falta "
                            "para valorar este criterio.",
                            "insufficient_data": "Confirma la información que falta.",
                        }[etiqueta]
                        + " "
                        + elemento["recomendacion"]
                    )
        return resultado | {
            "recommendations": relacionadas[:3],
            "criteria_analysis": criterios,
            "next_steps": [elemento["recomendacion"] for elemento in criterios],
            "explanation_kind": "learned_with_grounded_explanation"
            if estado["quality_approved"]
            else "structured",
            "recommendation_training": estado,
        }
