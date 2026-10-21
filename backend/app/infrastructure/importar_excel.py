"""Ejecutar desde backend: python -m app.infrastructure.importar_excel archivo.xlsx."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from app.adapters.contratos import externalizar_registro
from app.adapters.output.excel import leer_carreras
from app.adapters.output.importador import importar_libro
from app.infrastructure.base_datos import crear_sesiones
from app.infrastructure.configuracion import Configuracion


def principal():
    argumentos_cli = argparse.ArgumentParser(description="Importar catálogo PoC validado")
    argumentos_cli.add_argument("archivo", type=Path)
    argumentos_cli.add_argument(
        "--instantanea",
        "--snapshot",
        dest="instantanea",
        type=Path,
        help="Exportar solo una demo; no escribe en BD",
    )
    argumentos = argumentos_cli.parse_args()
    if argumentos.instantanea:
        carreras = leer_carreras(argumentos.archivo)
        argumentos.instantanea.parent.mkdir(parents=True, exist_ok=True)
        argumentos.instantanea.write_text(
            json.dumps(
                [externalizar_registro(asdict(c)) for c in carreras],
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )
        print(f"Demo: {len(carreras)} ofertas; no se escribió en PostgreSQL")
    else:
        with crear_sesiones(Configuracion())() as sesion:
            print(importar_libro(argumentos.archivo, sesion))


if __name__ == "__main__":
    principal()
