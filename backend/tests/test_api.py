from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.adapters.input.http import obtener_catalogo
from app.adapters.output.repositorios_carreras import RepositorioCarrerasJson
from app.infrastructure.configuracion import Configuracion
from app.infrastructure.principal import crear_aplicacion
from app.ports.repositorio_carreras import ConsultaCatalogo


def cliente():
    return TestClient(
        crear_aplicacion(
            Configuracion(modo_datos="demo", ruta_catalogo_json=Path("data/catalogo.json"))
        )
    )


def test_catalogo_busqueda_paginacion_filtros_ficha():
    with cliente() as c:
        datos = c.get("/api/carreras").json()
        assert datos["total"] == 35 and len(datos["items"]) == 12
        assert datos["data_mode"] == "demo"
        second = c.get("/api/carreras?pagina=2").json()
        assert len(second["items"]) == 12
        assert len(c.get("/api/carreras?pagina=3").json()["items"]) == 11
        assert c.get("/api/carreras/C20").json()["institution"] == "PUCP"
        assert c.get("/api/carreras/C24").json()["monthly_cost_pen"] is None
        assert not {r["id"] for r in datos["items"]} & {r["id"] for r in second["items"]}
        resultado = c.get(
            "/api/carreras",
            params={
                "q": "ingenieria",
                "modalidad": "Virtual",
                "ubicacion": "Virtual",
                "tipo": "Universitaria",
            },
        )
        assert resultado.json()["total"] == 1
        assert resultado.json()["items"][0]["id"] == "C16"
        assert c.get("/api/carreras?q=sin-coincidencias").json()["total"] == 0
        assert c.get("/api/carreras/C05").json()["monthly_cost_pen"] == "0"
        assert len(c.get("/api/carreras/C01").json()["sources"]) == 6
        assert c.get("/api/carreras/inexistente").status_code == 404
        assert c.get("/api/carreras?pagina=0").status_code == 422
        assert c.get("/api/carreras?limite=101").status_code == 422
        assert "Virtual" in c.get("/api/filtros").json()["modalidad"]


def test_retiradas_y_fallo_sql_sin_sustitucion():
    repo = RepositorioCarrerasJson(Path("data/catalogo.json"))
    from dataclasses import replace

    repo.carreras = [replace(repo.carreras[0], activa=False)]
    assert repo.listar(ConsultaCatalogo())[1] == 0
    assert repo.obtener("C01") is None
    app = crear_aplicacion(
        Configuracion(modo_datos="demo", ruta_catalogo_json=Path("data/catalogo.json"))
    )

    def averiado():
        raise OperationalError("SECRET", {}, Exception("SECRET"))

    app.dependency_overrides[obtener_catalogo] = averiado
    with TestClient(app) as c:
        respuesta = c.get("/api/carreras")
        assert respuesta.status_code == 503
        assert "SECRET" not in respuesta.text


def test_cors():
    with cliente() as c:
        correcto = c.options(
            "/api/carreras",
            headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
        )
        assert correcto.headers["access-control-allow-origin"] == "http://localhost:5173"
        denied = c.options(
            "/api/carreras",
            headers={"Origin": "https://unknown.example", "Access-Control-Request-Method": "GET"},
        )
        assert "access-control-allow-origin" not in denied.headers
