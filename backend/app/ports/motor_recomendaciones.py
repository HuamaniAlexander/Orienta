from typing import Protocol

from app.domain.carrera import Carrera


class MotorRecomendaciones(Protocol):
    def analizar(
        self, izquierda: Carrera, derecha: Carrera, preferencias: dict
    ) -> tuple[dict, dict]: ...
