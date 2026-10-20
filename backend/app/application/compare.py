from app.application.catalog import Catalog
from app.domain.comparison import InvalidComparison, compare


class CompareCareers:
    def __init__(self, catalog: Catalog):
        self.catalog = catalog

    def execute(self, ids: list[str]):
        if len(ids) != 2 or len(set(ids)) != 2:
            raise InvalidComparison("Selecciona exactamente dos alternativas diferentes")
        return compare(*(self.catalog.detail(id) for id in ids))
