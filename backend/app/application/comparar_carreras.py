from app.application.catalogo import Catalogo
from app.domain.comparacion import ComparacionInvalida, comparar


class CompararCarreras:
    def __init__(self, catalogo: Catalogo):
        self.catalogo = catalogo

    def ejecutar(self, identificadores: list[str]):
        if len(identificadores) != 2 or len(set(identificadores)) != 2:
            raise ComparacionInvalida("Selecciona exactamente dos alternativas diferentes")
        return comparar(*(self.catalogo.detalle(id) for id in identificadores))
