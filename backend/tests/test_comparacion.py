from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.adapters.output.excel import leer_carreras
from app.domain.comparacion import ComparacionInvalida, comparar
from app.infrastructure.configuracion import Configuracion
from app.infrastructure.principal import crear_aplicacion


def test_dos_carreras_distintas_y_datos_faltantes(libro_datos):
    izquierda = leer_carreras(libro_datos())[0]
    with pytest.raises(ComparacionInvalida):
        comparar(izquierda, izquierda)
    derecha = replace(
        izquierda,
        id="C02",
        modalidad="Virtual",
        duracion_meses=None,
        costo_mensual_soles=Decimal(0),
    )
    resultado = comparar(izquierda, derecha)
    assert resultado.diferencia_duracion_meses is None
    assert resultado.diferencia_costo_mensual_soles == Decimal(-775)
    assert comparar(derecha, izquierda).diferencia_costo_mensual_soles == Decimal(775)


def test_contrato_comparacion():
    with TestClient(
        crear_aplicacion(
            Configuracion(modo_datos="demo", ruta_catalogo_json=Path("data/catalogo.json"))
        )
    ) as cliente:
        for identificadores in [[], ["C01"], ["C01", "C01"], ["C01", "C02", "C03"]]:
            assert (
                cliente.post("/api/comparaciones", json={"career_ids": identificadores}).status_code
                == 422
            )
        resultado = cliente.post("/api/comparaciones", json={"career_ids": ["C01", "C05"]})
        assert resultado.status_code == 200
        assert resultado.json()["monthly_cost_difference_pen"] == "-775"
        assert resultado.json()["duration_difference_months"] == 0
        assert (
            cliente.post("/api/comparaciones", json={"career_ids": ["C01", "no"]}).status_code
            == 404
        )
