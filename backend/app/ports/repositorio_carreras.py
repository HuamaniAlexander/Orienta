from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.domain.carrera import Carrera


@dataclass(frozen=True)
class ConsultaCatalogo:
    q: str = ""
    tipo: str = ""
    modalidad: str = ""
    ubicacion: str = ""
    pagina: int = 1
    limite: int = 12

    def __post_init__(self):
        if self.pagina < 1 or not 1 <= self.limite <= 100:
            raise ValueError("Paginación fuera de rango")


class RepositorioCarreras(Protocol):
    def listar(self, consulta: ConsultaCatalogo) -> tuple[list[Carrera], int]: ...
    def obtener(self, id: str) -> Carrera | None: ...
    def facetas(self) -> dict[str, list[str]]: ...
