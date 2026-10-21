import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.adapters.output.excel import leer_carreras
from app.adapters.output.modelos import FilaCarrera, FilaFuente, FilaImportacion, FilaInstitucion
from app.domain.carrera import Carrera, normalizar


def importar_libro(ruta: Path, sesion: Session) -> dict[str, int | bool]:
    # Validar todas las filas antes de abrir la transacción de escritura.
    huella_contenido = sha256(ruta.read_bytes()).hexdigest()
    carreras = leer_carreras(ruta)
    return importar_carreras(carreras, huella_contenido, ruta.name, sesion)


def importar_carreras(
    carreras: list[Carrera],
    huella_contenido: str,
    nombre_archivo: str,
    sesion: Session,
    *,
    sustituir_catalogo: bool = False,
) -> dict[str, int | bool]:
    if (
        not carreras
        or len({c.id for c in carreras}) != len(carreras)
        or len({c.identidad for c in carreras}) != len(carreras)
    ):
        raise ValueError("El catálogo está vacío o contiene duplicados")
    with sesion.begin():
        # Serializar importaciones concurrentes; las restricciones únicas protegen la integridad.
        if sesion.bind.dialect.name == "postgresql":
            from sqlalchemy import text as texto

            sesion.execute(texto("SELECT pg_advisory_xact_lock(710013)"))
        anterior = sesion.scalar(
            select(FilaImportacion).where(FilaImportacion.sha256 == huella_contenido)
        )
        if anterior:
            return {"rows": anterior.cantidad_filas, "unchanged": True}
        lote = FilaImportacion(
            sha256=huella_contenido,
            nombre_archivo=nombre_archivo,
            cantidad_filas=len(carreras),
            fecha_importacion=datetime.now(timezone.utc),
        )
        sesion.add(lote)
        sesion.flush()
        if sustituir_catalogo:
            sesion.execute(update(FilaCarrera).values(activa=False))
        for carrera in carreras:
            institucion = sesion.scalar(
                select(FilaInstitucion).where(FilaInstitucion.nombre == carrera.institucion)
            )
            if institucion is None:
                institucion = FilaInstitucion(nombre=carrera.institucion)
                sesion.add(institucion)
                sesion.flush()
            fila = sesion.get(FilaCarrera, carrera.id)
            clave_identidad = json.dumps(carrera.identidad, ensure_ascii=False)
            conflicto = sesion.scalar(
                select(FilaCarrera).where(
                    FilaCarrera.clave_identidad == clave_identidad, FilaCarrera.id != carrera.id
                )
            )
            if conflicto:
                raise ValueError(f"Identidad ya asociada al código {conflicto.id}")
            if fila is None:
                fila = FilaCarrera(id=carrera.id)
                sesion.add(fila)
            for clave in (
                "nombre",
                "tipo_formacion",
                "modalidad",
                "ubicacion",
                "duracion_meses",
                "costo_mensual_soles",
                "requisitos",
                "campo_laboral",
                "fecha_revision",
                "activa",
                "detalles",
            ):
                setattr(fila, clave, getattr(carrera, clave))
            fila.id_institucion = institucion.id
            fila.nombre_busqueda = normalizar(carrera.nombre)
            fila.texto_busqueda = normalizar(
                " ".join(
                    [
                        carrera.nombre,
                        carrera.institucion,
                        carrera.detalles.get("area_conocimiento", ""),
                    ]
                )
            )
            fila.clave_identidad = clave_identidad
            fila.id_importacion = lote.id
            fila.fuentes = [
                FilaFuente(
                    campo=s.campo,
                    referencia=s.referencia,
                    estado=s.estado or "Sin estado registrado",
                )
                for s in carrera.fuentes
            ]
            sesion.flush()
    return {"rows": len(carreras), "unchanged": False}
