from fastapi import Request

from app.adapters.output.repositories import JsonCareerRepository, SqlCareerRepository
from app.application.catalog import Catalog


def catalog_dependency(request: Request):
    if request.app.state.settings.data_mode == "demo":
        yield Catalog(JsonCareerRepository(request.app.state.settings.demo_path))
    else:
        with request.app.state.sessions() as session:
            yield Catalog(SqlCareerRepository(session))
