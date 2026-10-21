from dataclasses import replace
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.adapters.output.excel import leer_carreras
from app.adapters.output.importador import importar_libro
from app.adapters.output.modelos import FilaCarrera, FilaFuente, FilaImportacion
from app.adapters.output.repositorios_carreras import RepositorioCarrerasSql
from app.infrastructure.configuracion import Configuracion
from app.infrastructure.principal import crear_aplicacion
from app.ports.repositorio_carreras import ConsultaCatalogo


def test_http_con_persistencia_sql(base_datos, libro_datos):
    with Session(base_datos) as sesion:
        importar_libro(libro_datos([{}, {"id_carrera": "C02", "modalidad": "Virtual"}]), sesion)
    if base_datos.dialect.name != "postgresql":
        pytest.skip("El recorrido SQL HTTP requiere TEST_DATABASE_URL de PostgreSQL")
    configuracion = Configuracion(
        modo_datos="postgres", url_base_datos=base_datos.url.render_as_string(hide_password=False)
    )
    with TestClient(crear_aplicacion(configuracion)) as cliente:
        datos = cliente.get(
            "/api/carreras", params={"q": "ingenieria", "modalidad": "Virtual"}
        ).json()
        assert datos["data_mode"] == "postgres"
        assert datos["total"] == 1 and datos["items"][0]["id"] == "C02"
        assert cliente.get("/api/carreras/C01").status_code == 200
        resultado = cliente.post("/api/comparaciones", json={"career_ids": ["C01", "C02"]})
        assert resultado.status_code == 200
        assert resultado.json()["duration_difference_months"] == 0


def test_dato_faltante_distinto_de_cero(libro_datos):
    c = leer_carreras(libro_datos([{"costo_mensual_soles": 0, "duracion_meses": None}]))[0]
    assert c.costo_mensual_soles == Decimal(0)
    assert c.duracion_meses is None
    assert "Estimado" in c.fuentes[3].estado
    assert (
        leer_carreras(libro_datos([{"costo_mensual_soles": None}]))[0].costo_mensual_soles is None
    )


@pytest.mark.parametrize(
    "cambios",
    [
        {"costo_mensual_soles": -1},
        {"costo_mensual_soles": "NaN"},
        {"duracion_meses": 1.5},
        {"duracion_meses": 0},
        {"carrera": ""},
        {"fecha_revision": "no es fecha"},
    ],
)
def test_libro_invalido(libro_datos, cambios):
    with pytest.raises(ValueError, match="Fila 2"):
        leer_carreras(libro_datos([cambios]))


def test_duplicados_y_ofertas_distintas(libro_datos):
    with pytest.raises(ValueError, match="duplicada"):
        leer_carreras(libro_datos([{}, {"id_carrera": "C02"}]))
    assert len(leer_carreras(libro_datos([{}, {"id_carrera": "C02", "modalidad": "Virtual"}]))) == 2
    c = leer_carreras(libro_datos())[0]
    with pytest.raises(ValueError):
        replace(c, costo_mensual_soles=Decimal("-1"))


def test_migracion_importacion_repetible_y_transaccion(base_datos, libro_datos):
    with Session(base_datos) as sesion:
        ruta = libro_datos()
        assert importar_libro(ruta, sesion) == {"rows": 1, "unchanged": False}
        assert importar_libro(ruta, sesion)["unchanged"]
        assert sesion.scalar(select(func.count()).select_from(FilaCarrera)) == 1
        assert sesion.scalar(select(func.count()).select_from(FilaFuente)) == 6
        sesion.rollback()
        ruta = libro_datos([{"id_carrera": "C02", "carrera": "Derecho"}, {"id_carrera": "C03"}])
        with pytest.raises(ValueError, match="Identidad"):
            importar_libro(ruta, sesion)
        assert sesion.get(FilaCarrera, "C02") is None
        assert sesion.scalar(select(func.count()).select_from(FilaImportacion)) == 1


def test_repositorio_sql_filtros_y_retiradas(base_datos, libro_datos):
    with Session(base_datos) as sesion:
        importar_libro(
            libro_datos(
                [{}, {"id_carrera": "C02", "modalidad": "Virtual", "ubicacion": "Virtual"}]
            ),
            sesion,
        )
        repo = RepositorioCarrerasSql(sesion)
        elementos, total = repo.listar(
            ConsultaCatalogo(q="ingenieria", modalidad="Virtual", ubicacion="Virtual")
        )
        assert total == 1 and elementos[0].id == "C02"
        assert len(elementos[0].fuentes) == 6
        assert repo.listar(ConsultaCatalogo(q="%"))[1] == 0
        assert repo.listar(ConsultaCatalogo(q="' OR 1=1 --"))[1] == 0
        sesion.get(FilaCarrera, "C02").activa = False
        sesion.commit()
        assert repo.obtener("C02") is None
        assert repo.listar(ConsultaCatalogo())[1] == 1
        assert "Virtual" not in repo.facetas()["modalidad"]
