import json
from pathlib import Path

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from alembic import command
from app.adapters.output.importador import importar_carreras, importar_libro
from app.adapters.output.modelos import FilaCarrera
from app.adapters.output.repositorios_carreras import RepositorioCarrerasJson
from app.infrastructure.configuracion import Configuracion
from app.infrastructure.principal import crear_aplicacion


def test_migracion_reversible_conserva_registros(base_datos, libro_datos):
    with Session(base_datos) as sesion:
        importar_libro(libro_datos(), sesion)
        nombre = sesion.get(FilaCarrera, "C01").nombre
    configuracion = Config("alembic.ini")
    command.downgrade(configuracion, "0001")
    with base_datos.connect() as conexion:
        assert conexion.scalar(text("SELECT name FROM academic_offers WHERE id = 'C01'")) == nombre
        assert conexion.scalar(text("SELECT COUNT(*) FROM sources")) == 6
    command.upgrade(configuracion, "head")
    with Session(base_datos) as sesion:
        carrera = sesion.get(FilaCarrera, "C01")
        assert carrera.nombre == nombre
        assert len(carrera.fuentes) == 6


def test_respuestas_api_conservan_contrato_anterior(base_datos):
    if base_datos.dialect.name != "postgresql":
        pytest.skip("La comparación del contrato completo requiere PostgreSQL")
    repositorio = RepositorioCarrerasJson(Path("data/catalogo.json"))
    with Session(base_datos) as sesion:
        importar_carreras(repositorio.carreras, "contrato-v1", "catalogo.json", sesion)
    configuracion = Configuracion(
        modo_datos="postgres",
        url_base_datos=base_datos.url.render_as_string(hide_password=False),
    )
    referencia = json.loads(Path("tests/datos/contratos_api_v1.json").read_text(encoding="utf8"))
    with TestClient(crear_aplicacion(configuracion)) as cliente:
        for ruta, esperado in referencia.items():
            respuesta = (
                cliente.get(ruta)
                if ruta.startswith(("/api/carreras", "/api/filtros"))
                else cliente.post(ruta, json={"career_ids": ["C01", "C02"]})
            )
            assert respuesta.status_code == 200, respuesta.text
            assert respuesta.json() == esperado, ruta


def test_documentacion_y_errores_conservan_claves_externas():
    with TestClient(crear_aplicacion(Configuracion(modo_datos="demo"))) as cliente:
        esquema = cliente.get("/openapi.json").json()
        solicitud = esquema["components"]["schemas"]["SolicitudComparacion"]
        assert "career_ids" in solicitud["properties"]
        assert "ids_carreras" not in solicitud["properties"]
        respuesta = cliente.post("/api/comparaciones", json={})
        assert respuesta.status_code == 422
        assert respuesta.json()["detail"][0]["loc"] == ["body", "career_ids"]
