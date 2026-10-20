from fastapi import APIRouter, Depends, Query, Request

from app.adapters.input.esquemas import (
    RespuestaAnalisis,
    RespuestaCarrera,
    RespuestaCatalogo,
    RespuestaComparacion,
    SolicitudAnalisis,
    SolicitudComparacion,
)
from app.application.analizar_comparacion import AnalizarComparacion
from app.application.catalogo import Catalogo
from app.application.comparar_carreras import CompararCarreras
from app.infrastructure.dependencias import obtener_catalogo
from app.ports.repositorio_carreras import ConsultaCatalogo

enrutador = APIRouter(prefix="/api")


@enrutador.post(
    "/comparaciones/analisis",
    operation_id="analysis_api_comparaciones_analisis_post",
    response_model=RespuestaAnalisis,
)
def analisis(
    cuerpo: SolicitudAnalisis, solicitud: Request, catalogo: Catalogo = Depends(obtener_catalogo)
):
    resultado = AnalizarComparacion(
        catalogo,
        solicitud.app.state.servicio_analisis,
        solicitud.app.state.servicio_recomendaciones,
    ).ejecutar(
        cuerpo.ids_carreras, cuerpo.preferencias.model_dump(exclude_none=True, by_alias=True)
    )
    resultado["recommendations"] = [
        RespuestaCarrera.model_validate(c) for c in resultado["recommendations"]
    ]
    return RespuestaAnalisis(**resultado)


@enrutador.post(
    "/comparaciones",
    operation_id="comparison_api_comparaciones_post",
    response_model=RespuestaComparacion,
)
def comparacion(cuerpo: SolicitudComparacion, catalogo: Catalogo = Depends(obtener_catalogo)):
    return RespuestaComparacion.model_validate(
        CompararCarreras(catalogo).ejecutar(cuerpo.ids_carreras)
    )


@enrutador.get("/salud", operation_id="health_api_salud_get")
def salud(solicitud: Request):
    return {"status": "ok", "data_mode": solicitud.app.state.configuracion.modo_datos}


@enrutador.get(
    "/filtros", operation_id="filters_api_filtros_get", response_model=dict[str, list[str]]
)
def filtros(catalogo: Catalogo = Depends(obtener_catalogo)):
    return catalogo.filtros()


@enrutador.get(
    "/carreras", operation_id="careers_api_carreras_get", response_model=RespuestaCatalogo
)
def carreras(
    solicitud: Request,
    q: str = Query("", max_length=150),
    tipo: str = Query("", max_length=60),
    modalidad: str = Query("", max_length=100),
    ubicacion: str = Query("", max_length=200),
    pagina: int = Query(1, ge=1, le=10000),
    limite: int = Query(12, ge=1, le=100),
    catalogo: Catalogo = Depends(obtener_catalogo),
):
    elementos, total = catalogo.buscar(
        ConsultaCatalogo(q, tipo, modalidad, ubicacion, pagina, limite)
    )
    return RespuestaCatalogo(
        elementos=[RespuestaCarrera.model_validate(c) for c in elementos],
        total=total,
        pagina=pagina,
        limite=limite,
        modo_datos=solicitud.app.state.configuracion.modo_datos,
    )


@enrutador.get(
    "/carreras/{id}", operation_id="detail_api_carreras__id__get", response_model=RespuestaCarrera
)
def detalle(id: str, catalogo: Catalogo = Depends(obtener_catalogo)):
    return RespuestaCarrera.model_validate(catalogo.detalle(id))
