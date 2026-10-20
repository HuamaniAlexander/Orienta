from typing import Protocol

from app.domain.carrera import Carrera


class AnalisisNoDisponible(Exception):
    pass


class MotorAnalisis(Protocol):
    def analizar(self, izquierda: Carrera, derecha: Carrera) -> dict: ...
