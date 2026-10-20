from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.domain.career import Career


@dataclass(frozen=True)
class CatalogQuery:
    q: str = ""
    tipo: str = ""
    modalidad: str = ""
    ubicacion: str = ""
    pagina: int = 1
    limite: int = 12

    def __post_init__(self):
        if self.pagina < 1 or not 1 <= self.limite <= 100:
            raise ValueError("Paginación fuera de rango")


class CareerRepository(Protocol):
    def list(self, query: CatalogQuery) -> tuple[list[Career], int]: ...
    def get(self, id: str) -> Career | None: ...
    def facets(self) -> dict[str, list[str]]: ...
