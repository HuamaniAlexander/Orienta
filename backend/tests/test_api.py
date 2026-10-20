from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.adapters.input.http import catalog_dependency
from app.adapters.output.repositories import JsonCareerRepository
from app.infrastructure.main import create_app
from app.infrastructure.settings import Settings
from app.ports.careers import CatalogQuery


def client():
    return TestClient(create_app(Settings(data_mode="demo")))


def test_catalog_search_pagination_filters_detail():
    with client() as c:
        data = c.get("/api/carreras").json()
        assert data["total"] == 35 and len(data["items"]) == 12
        assert data["data_mode"] == "demo"
        second = c.get("/api/carreras?pagina=2").json()
        assert len(second["items"]) == 12
        assert len(c.get("/api/carreras?pagina=3").json()["items"]) == 11
        assert c.get("/api/carreras/C20").json()["institution"] == "PUCP"
        assert c.get("/api/carreras/C24").json()["monthly_cost_pen"] is None
        assert not {r["id"] for r in data["items"]} & {r["id"] for r in second["items"]}
        result = c.get(
            "/api/carreras",
            params={
                "q": "ingenieria",
                "modalidad": "Virtual",
                "ubicacion": "Virtual",
                "tipo": "Universitaria",
            },
        )
        assert result.json()["total"] == 1
        assert result.json()["items"][0]["id"] == "C16"
        assert c.get("/api/carreras?q=sin-coincidencias").json()["total"] == 0
        assert c.get("/api/carreras/C05").json()["monthly_cost_pen"] == "0"
        assert len(c.get("/api/carreras/C01").json()["sources"]) == 6
        assert c.get("/api/carreras/inexistente").status_code == 404
        assert c.get("/api/carreras?pagina=0").status_code == 422
        assert c.get("/api/carreras?limite=101").status_code == 422
        assert "Virtual" in c.get("/api/filtros").json()["modalidad"]


def test_retired_and_sql_failure_are_not_fallbacks():
    repo = JsonCareerRepository(Path("data/catalog.json"))
    from dataclasses import replace

    repo.careers = [replace(repo.careers[0], active=False)]
    assert repo.list(CatalogQuery())[1] == 0
    assert repo.get("C01") is None
    app = create_app(Settings(data_mode="demo"))

    def broken():
        raise OperationalError("SECRET", {}, Exception("SECRET"))

    app.dependency_overrides[catalog_dependency] = broken
    with TestClient(app) as c:
        response = c.get("/api/carreras")
        assert response.status_code == 503
        assert "SECRET" not in response.text


def test_cors():
    with client() as c:
        ok = c.options(
            "/api/carreras",
            headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
        )
        assert ok.headers["access-control-allow-origin"] == "http://localhost:5173"
        denied = c.options(
            "/api/carreras",
            headers={"Origin": "https://unknown.example", "Access-Control-Request-Method": "GET"},
        )
        assert "access-control-allow-origin" not in denied.headers
