from fastapi import Request

from app.adapters.output.repositorios_carreras import (
    RepositorioCarrerasJson,
    RepositorioCarrerasSql,
)
from app.application.catalogo import Catalogo


def obtener_catalogo(solicitud: Request):
    if solicitud.app.state.configuracion.modo_datos == "demo":
        yield Catalogo(
            RepositorioCarrerasJson(solicitud.app.state.configuracion.ruta_catalogo_json)
        )
    else:
        with solicitud.app.state.sesiones() as sesion:
            yield Catalogo(RepositorioCarrerasSql(sesion))
