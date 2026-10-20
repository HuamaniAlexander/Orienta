from app.application.catalogo import CarreraNoEncontrada, Catalogo
from app.application.comparar_carreras import CompararCarreras
from app.domain.analisis_criterios import analizar_criterios
from app.ports.motor_analisis import MotorAnalisis
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
        resultado = self.servicio.analizar(comparacion.izquierda, comparacion.derecha)
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
