import json
from hashlib import sha256
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.adapters.output.catalogo_completo import leer_catalogo_completo
from app.adapters.output.importador import importar_carreras
from app.adapters.output.modelos import FilaCarrera, FilaFuente
from app.infrastructure.configuracion import Configuracion
from app.infrastructure.principal import crear_aplicacion

RUTA = Path("data/catalogo_lima_norte_2026.json")


def test_catalogo_entregado_no_pierde_programas_ni_procedencia():
    original = json.loads(RUTA.read_text(encoding="utf-8"))
    carreras = leer_catalogo_completo(RUTA)
    assert len(carreras) == 405
    assert len({c.institucion for c in carreras}) == 25
    assert len({c.detalles["carrera_id"] for c in carreras}) == 196
    assert {c.id for c in carreras} == {p["id"] for p in original["programas"]}
    assert all(len(c.fuentes) == 6 for c in carreras)
    for carrera, programa in zip(carreras, original["programas"], strict=True):
        assert all(carrera.detalles[clave] == valor for clave, valor in programa.items())
        assert "Estimación" in next(f.estado for f in carrera.fuentes if f.campo == "Costo")


def test_importacion_completa_api_filtros_comparacion_y_repeticion(base_datos, request):
    if base_datos.dialect.name != "postgresql":
        pytest.skip("Integración completa en PostgreSQL")

    def limpiar_base_exclusiva_pruebas():
        with Session(base_datos) as sesion, sesion.begin():
            sesion.execute(delete(FilaFuente))
            sesion.execute(delete(FilaCarrera))

    request.addfinalizer(limpiar_base_exclusiva_pruebas)
    carreras = leer_catalogo_completo(RUTA)
    huella = sha256(RUTA.read_bytes()).hexdigest()
    with Session(base_datos) as sesion:
        assert (
            importar_carreras(carreras, huella, RUTA.name, sesion, sustituir_catalogo=True)["rows"]
            == 405
        )
        assert importar_carreras(carreras, huella, RUTA.name, sesion, sustituir_catalogo=True)[
            "unchanged"
        ]
        assert sesion.scalar(select(func.count()).select_from(FilaCarrera)) == 405
    configuracion = Configuracion(
        modo_datos="postgres", url_base_datos=base_datos.url.render_as_string(hide_password=False)
    )
    with TestClient(crear_aplicacion(configuracion)) as cliente:
        recibidos = []
        for pagina in range(1, 6):
            respuesta = cliente.get("/api/carreras", params={"pagina": pagina, "limite": 100})
            assert respuesta.status_code == 200
            assert respuesta.json()["total"] == 405
            recibidos.extend(c["id"] for c in respuesta.json()["items"])
        assert set(recibidos) == {c.id for c in carreras}
        instituciones = cliente.get("/api/instituciones").json()
        assert len(instituciones) == 25
        assert sum(i["ofertas"] for i in instituciones) == 405
        assert len(cliente.get("/api/filtros").json()["institucion"]) == 25
        for consulta, esperado in [
            ({"gestion": "publica"}, 86),
            ({"gestion": "privada"}, 319),
            ({"institucion": "Universidad Privada del Norte"}, 43),
            ({"q": "SENATI"}, 14),
        ]:
            assert cliente.get("/api/carreras", params=consulta).json()["total"] == esperado
        filtros = {"gestion": "publica", "costo_maximo": 0}
        for elemento in cliente.get("/api/carreras", params=filtros).json()["items"]:
            assert elemento["detalles"]["gestion"] == "publica"
            assert float(elemento["monthly_cost_pen"]) <= 0
        ids = [carreras[0].id, carreras[-1].id]
        assert len(ids[0]) > 30
        assert (
            cliente.get(f"/api/carreras/{ids[0]}").json()["detalles"]["carrera_id"]
            == carreras[0].detalles["carrera_id"]
        )
        assert cliente.post("/api/comparaciones", json={"career_ids": ids}).status_code == 200
        analisis = cliente.post("/api/comparaciones/analisis", json={"career_ids": ids})
        assert analisis.status_code == 200, analisis.text
        assert len(analisis.json()["criteria_analysis"]) == 6
        assert analisis.json()["quality_approved"] is False
        assert analisis.json()["metrics"] == {}


def test_modo_json_tambien_publica_el_catalogo_completo():
    configuracion = Configuracion(modo_datos="demo", ruta_catalogo_json=RUTA)
    with TestClient(crear_aplicacion(configuracion)) as cliente:
        assert cliente.get("/api/carreras").json()["total"] == 405
        assert len(cliente.get("/api/instituciones").json()) == 25
