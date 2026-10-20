import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.adapters.contratos import internalizar_registro
from app.adapters.output.modelos import FilaCarrera, FilaInstitucion
from app.domain.carrera import Carrera, Fuente, normalizar
from app.ports.repositorio_carreras import ConsultaCatalogo

FACETAS_DETALLES = {
    "gestion": "gestion",
    "area": "area_conocimiento",
    "institucion": "nombre_institucion",
}

FACETAS = {"tipo": "tipo_formacion", "modalidad": "modalidad", "ubicacion": "ubicacion"}


class RepositorioCarrerasJson:
    """Adaptador JSON explícito de solo lectura; no sustituye fallos de PostgreSQL."""

    def __init__(self, ruta: Path):
        contenido = json.loads(ruta.read_text(encoding="utf-8"))
        if isinstance(contenido, dict) and "programas" in contenido:
            from app.adapters.output.catalogo_completo import leer_catalogo_completo

            self.carreras = leer_catalogo_completo(ruta)
            return
        datos = internalizar_registro(contenido)
        self.carreras = [
            Carrera(
                **(
                    fila
                    | {
                        "costo_mensual_soles": Decimal(fila["costo_mensual_soles"])
                        if fila["costo_mensual_soles"] is not None
                        else None,
                        "fecha_revision": date.fromisoformat(fila["fecha_revision"])
                        if fila["fecha_revision"]
                        else None,
                        "fuentes": tuple(Fuente(**s) for s in fila["fuentes"]),
                    }
                )
            )
            for fila in datos
        ]

    def listar(self, consulta: ConsultaCatalogo):
        resultado = [
            c
            for c in self.carreras
            if c.activa
            and normalizar(consulta.q)
            in normalizar(
                " ".join([c.nombre, c.institucion, c.detalles.get("area_conocimiento", "")])
            )
            and all(
                not getattr(consulta, clave) or c.detalles.get(atributo) == getattr(consulta, clave)
                for clave, atributo in FACETAS_DETALLES.items()
            )
            and (
                consulta.costo_maximo is None
                or c.costo_mensual_soles is not None
                and c.costo_mensual_soles <= consulta.costo_maximo
            )
            and all(
                not getattr(consulta, clave) or getattr(c, atributo) == getattr(consulta, clave)
                for clave, atributo in FACETAS.items()
            )
        ]
        resultado.sort(key=lambda c: (normalizar(c.nombre), c.institucion, c.id))
        inicio = (consulta.pagina - 1) * consulta.limite
        return resultado[inicio : inicio + consulta.limite], len(resultado)

    def obtener(self, id: str):
        return next((c for c in self.carreras if c.id == id and c.activa), None)

    def facetas(self):
        return {
            clave: sorted(
                {getattr(c, atributo) for c in self.carreras if c.activa and getattr(c, atributo)}
            )
            for clave, atributo in FACETAS.items()
        } | {
            clave: sorted(
                {
                    c.detalles[atributo]
                    for c in self.carreras
                    if c.activa and c.detalles.get(atributo)
                }
            )
            for clave, atributo in FACETAS_DETALLES.items()
            if any(c.detalles.get(atributo) for c in self.carreras)
        }


def convertir_al_dominio(fila: FilaCarrera) -> Carrera:
    return Carrera(
        id=fila.id,
        nombre=fila.nombre,
        institucion=fila.institucion.nombre,
        tipo_formacion=fila.tipo_formacion,
        modalidad=fila.modalidad,
        ubicacion=fila.ubicacion,
        duracion_meses=fila.duracion_meses,
        costo_mensual_soles=fila.costo_mensual_soles,
        requisitos=fila.requisitos,
        campo_laboral=fila.campo_laboral,
        fecha_revision=fila.fecha_revision,
        activa=fila.activa,
        detalles=fila.detalles or {},
        fuentes=tuple(Fuente(s.campo, s.referencia, s.estado) for s in fila.fuentes),
    )


class RepositorioCarrerasSql:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def listar(self, consulta: ConsultaCatalogo):
        condiciones = [FilaCarrera.activa.is_(True)]
        if consulta.q.strip():
            condiciones.append(
                FilaCarrera.texto_busqueda.contains(normalizar(consulta.q), autoescape=True)
            )
        for clave, atributo in FACETAS.items():
            if getattr(consulta, clave):
                condiciones.append(getattr(FilaCarrera, atributo) == getattr(consulta, clave))
        for clave, atributo in FACETAS_DETALLES.items():
            if getattr(consulta, clave):
                condiciones.append(
                    FilaCarrera.detalles[atributo].as_string() == getattr(consulta, clave)
                )
        if consulta.costo_maximo is not None:
            condiciones.append(FilaCarrera.costo_mensual_soles <= consulta.costo_maximo)
        total = self.sesion.scalar(
            select(func.count()).select_from(FilaCarrera).where(*condiciones)
        )
        filas = self.sesion.scalars(
            select(FilaCarrera)
            .join(FilaInstitucion)
            .where(*condiciones)
            .order_by(FilaCarrera.nombre_busqueda, FilaInstitucion.nombre, FilaCarrera.id)
            .offset((consulta.pagina - 1) * consulta.limite)
            .limit(consulta.limite)
        ).all()
        return [convertir_al_dominio(fila) for fila in filas], total

    def obtener(self, id: str):
        fila = self.sesion.scalar(
            select(FilaCarrera).where(FilaCarrera.id == id, FilaCarrera.activa.is_(True))
        )
        return convertir_al_dominio(fila) if fila else None

    def facetas(self):
        detalles = self.sesion.scalars(
            select(FilaCarrera.detalles).where(FilaCarrera.activa.is_(True))
        ).all()
        return {
            clave: list(
                self.sesion.scalars(
                    select(getattr(FilaCarrera, atributo))
                    .where(
                        FilaCarrera.activa.is_(True), getattr(FilaCarrera, atributo).is_not(None)
                    )
                    .distinct()
                    .order_by(getattr(FilaCarrera, atributo))
                )
            )
            for clave, atributo in FACETAS.items()
        } | {
            clave: sorted({d[atributo] for d in detalles if d.get(atributo)})
            for clave, atributo in FACETAS_DETALLES.items()
            if any(d.get(atributo) for d in detalles)
        }
