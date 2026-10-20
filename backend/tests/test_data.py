import os
from dataclasses import replace
from decimal import Decimal

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from alembic import command
from app.adapters.output.excel import read_careers
from app.adapters.output.importer import import_workbook
from app.adapters.output.models import CareerRow, ImportRow, SourceRow
from app.adapters.output.repositories import SqlCareerRepository
from app.infrastructure.main import create_app
from app.infrastructure.settings import Settings
from app.ports.careers import CatalogQuery


def test_http_with_sql_persistence(database, workbook):
    with Session(database) as session:
        import_workbook(workbook([{}, {"id_carrera": "C02", "modalidad": "Virtual"}]), session)
    if database.dialect.name != "postgresql":
        pytest.skip("El recorrido SQL HTTP requiere TEST_DATABASE_URL de PostgreSQL")
    settings = Settings(
        data_mode="postgres", database_url=database.url.render_as_string(hide_password=False)
    )
    with TestClient(create_app(settings)) as client:
        data = client.get(
            "/api/carreras", params={"q": "ingenieria", "modalidad": "Virtual"}
        ).json()
        assert data["data_mode"] == "postgres"
        assert data["total"] == 1 and data["items"][0]["id"] == "C02"
        assert client.get("/api/carreras/C01").status_code == 200
        result = client.post("/api/comparaciones", json={"career_ids": ["C01", "C02"]})
        assert result.status_code == 200
        assert result.json()["duration_difference_months"] == 0


def test_missing_and_zero_are_different(workbook):
    c = read_careers(workbook([{"costo_mensual_soles": 0, "duracion_meses": None}]))[0]
    assert c.monthly_cost_pen == Decimal(0)
    assert c.duration_months is None
    assert "Estimado" in c.sources[3].status
    assert read_careers(workbook([{"costo_mensual_soles": None}]))[0].monthly_cost_pen is None


@pytest.mark.parametrize(
    "changes",
    [
        {"costo_mensual_soles": -1},
        {"costo_mensual_soles": "NaN"},
        {"duracion_meses": 1.5},
        {"duracion_meses": 0},
        {"carrera": ""},
        {"fecha_revision": "no es fecha"},
    ],
)
def test_invalid_workbook(workbook, changes):
    with pytest.raises(ValueError, match="Fila 2"):
        read_careers(workbook([changes]))


def test_duplicates_and_distinct_offers(workbook):
    with pytest.raises(ValueError, match="duplicada"):
        read_careers(workbook([{}, {"id_carrera": "C02"}]))
    assert len(read_careers(workbook([{}, {"id_carrera": "C02", "modalidad": "Virtual"}]))) == 2
    c = read_careers(workbook())[0]
    with pytest.raises(ValueError):
        replace(c, monthly_cost_pen=Decimal("-1"))


@pytest.fixture
def database(tmp_path, monkeypatch):
    # CI supplies a real dedicated PostgreSQL database. Local fallback tests SQL behavior only.
    url = os.getenv("TEST_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("DATABASE_URL", url)
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    engine = create_engine(url)
    yield engine
    engine.dispose()
    command.downgrade(config, "base")


def test_migration_import_idempotence_and_transaction(database, workbook):
    with Session(database) as session:
        path = workbook()
        assert import_workbook(path, session) == {"rows": 1, "unchanged": False}
        assert import_workbook(path, session)["unchanged"]
        assert session.scalar(select(func.count()).select_from(CareerRow)) == 1
        assert session.scalar(select(func.count()).select_from(SourceRow)) == 6
        session.rollback()
        path = workbook([{"id_carrera": "C02", "carrera": "Derecho"}, {"id_carrera": "C03"}])
        with pytest.raises(ValueError, match="Identidad"):
            import_workbook(path, session)
        assert session.get(CareerRow, "C02") is None
        assert session.scalar(select(func.count()).select_from(ImportRow)) == 1


def test_sql_repository_filters_and_retired(database, workbook):
    with Session(database) as session:
        import_workbook(
            workbook([{}, {"id_carrera": "C02", "modalidad": "Virtual", "ubicacion": "Virtual"}]),
            session,
        )
        repo = SqlCareerRepository(session)
        items, total = repo.list(
            CatalogQuery(q="ingenieria", modalidad="Virtual", ubicacion="Virtual")
        )
        assert total == 1 and items[0].id == "C02"
        assert len(items[0].sources) == 6
        assert repo.list(CatalogQuery(q="%"))[1] == 0
        assert repo.list(CatalogQuery(q="' OR 1=1 --"))[1] == 0
        session.get(CareerRow, "C02").active = False
        session.commit()
        assert repo.get("C02") is None
        assert repo.list(CatalogQuery())[1] == 1
        assert "Virtual" not in repo.facets()["modalidad"]
