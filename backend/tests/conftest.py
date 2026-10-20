from pathlib import Path

import pytest
from openpyxl import Workbook

from app.adapters.output.excel import REQUIRED


@pytest.fixture
def workbook(tmp_path: Path):
    def make(rows=None):
        default = dict(
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
        wb = Workbook()
        ws = wb.active
        ws.title = "Carreras"
        headers = sorted(REQUIRED)
        ws.append(headers)
        for changes in rows if rows is not None else [{}]:
            row = default | changes
            ws.append([row[k] for k in headers])
        path = tmp_path / "catalog.xlsx"
        wb.save(path)
        wb.close()
        return path

    return make
