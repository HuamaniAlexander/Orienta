from typing import Protocol


class MotorPreferencias(Protocol):
    def predecir(self, caracteristicas: dict[str, float]) -> dict: ...


class RegistroPreferencias(Protocol):
    def guardar(self, registro: dict) -> str: ...
