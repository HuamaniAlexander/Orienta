from app.ports.careers import CareerRepository, CatalogQuery


class CareerNotFound(Exception):
    pass


class Catalog:
    def __init__(self, repository: CareerRepository):
        self.repository = repository

    def search(self, query: CatalogQuery):
        return self.repository.list(query)

    def detail(self, id: str):
        career = self.repository.get(id)
        if career is None or not career.active:
            raise CareerNotFound(id)
        return career

    def filters(self):
        return self.repository.facets()
