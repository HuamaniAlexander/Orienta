import os
from pathlib import Path

import pytest
from alembic.config import Config
from openpyxl import Workbook
from sqlalchemy import create_engine

from alembic import command
from app.adapters.output.excel import OBLIGATORIOS


@pytest.fixture
def libro_datos(tmp_path: Path):
    def crear(filas=None):
        predeterminado = dict(
            id_carrera="C01",
            carrera="Ingeniería de Software",
            institucion="UTP",
            duracion_meses=60,
            modalidad="Presencial",
            ubicacion="Campus Lima Norte",
            costo_mensual_soles=775,
            requisitos="Secundaria completa",
            campo_laboral="Software",
            estado_costo="Estimado; no tarifa oficial",
            estado_modalidad="Verificado",
            fuente_carrera="https://www.utp.edu.pe",
            fuente_costo="Referencia del usuario",
            fuente_requisitos=None,
            fecha_revision="2026-10-13",
            fuente_duracion="https://www.utp.edu.pe",
        )
        libro = Workbook()
        hoja = libro.active
        hoja.title = "Carreras"
        encabezados = sorted(OBLIGATORIOS)
        hoja.append(encabezados)
        for cambios in filas if filas is not None else [{}]:
            fila = predeterminado | cambios
            hoja.append([fila[k] for k in encabezados])
        ruta = tmp_path / "catalog.xlsx"
        libro.save(ruta)
        libro.close()
        return ruta

    return crear


@pytest.fixture
def base_datos(tmp_path, monkeypatch):
    # CI usa PostgreSQL exclusivo; SQLite local solo comprueba el comportamiento SQL.
    url = os.getenv("TEST_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("DATABASE_URL", url)
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    motor = create_engine(url)
    yield motor
    motor.dispose()
    command.downgrade(config, "base")
