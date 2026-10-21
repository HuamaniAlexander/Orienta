"""Revisión y exportación privada de capturas para entrenamiento offline."""

import argparse
import json
from pathlib import Path

from sqlalchemy import select

from app.adapters.output.modelos import FilaRegistroPreferencia
from app.infrastructure.base_datos import crear_sesiones
from app.infrastructure.configuracion import Configuracion


def principal():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="accion", required=True)
    revision = sub.add_parser("revisar")
    revision.add_argument("--id", required=True)
    revision.add_argument("--estado", choices=["aprobado", "rechazado"], required=True)
    revision.add_argument("--motivo", required=True)
    retirada = sub.add_parser("retirar")
    retirada.add_argument("--id", required=True)
    retirada.add_argument("--confirmar", action="store_true")
    exportacion = sub.add_parser("exportar")
    exportacion.add_argument("--salida", type=Path, required=True)
    argumentos = parser.parse_args()
    sesiones = crear_sesiones(Configuracion())
    with sesiones() as sesion, sesion.begin():
        if argumentos.accion == "retirar":
            if not argumentos.confirmar:
                raise ValueError("La retirada elimina el aporte; vuelve a ejecutar con --confirmar")
            fila = sesion.get(FilaRegistroPreferencia, argumentos.id)
            if fila is None:
                raise ValueError("Captura no encontrada")
            sesion.delete(fila)
            print("Aporte retirado; exclúyelo de exportaciones y reentrenamientos")
        elif argumentos.accion == "revisar":
            if len(argumentos.motivo.strip()) < 10:
                raise ValueError(
                    "Describe la comprobación de consentimiento, independencia y calidad"
                )
            fila = sesion.get(FilaRegistroPreferencia, argumentos.id)
            if fila is None:
                raise ValueError("Captura no encontrada")
            fila.estado_revision = argumentos.estado
            fila.datos = fila.datos | {"motivo_revision": argumentos.motivo.strip()}
            print("Estado de revisión actualizado")
        else:
            if argumentos.salida.exists():
                raise ValueError("Usa un archivo nuevo para no sobrescribir una exportación")
            filas = sesion.scalars(
                select(FilaRegistroPreferencia).where(
                    FilaRegistroPreferencia.estado_revision == "aprobado"
                )
            ).all()
            argumentos.salida.parent.mkdir(parents=True, exist_ok=True)
            argumentos.salida.write_text(
                "".join(
                    json.dumps(f.datos | {"estado_revision": f.estado_revision}, ensure_ascii=False)
                    + "\n"
                    for f in filas
                ),
                encoding="utf-8",
            )
            print(f"Capturas revisadas exportadas: {len(filas)}")


if __name__ == "__main__":
    principal()
