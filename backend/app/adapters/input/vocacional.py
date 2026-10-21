from dataclasses import asdict
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from pydantic.alias_generators import to_camel

from app.application.catalogo import Catalogo
from app.application.recomendar_preferencia import RecomendarPreferencia
from app.domain.cuestionario import VERSION_CUESTIONARIO, preguntas_generales
from app.infrastructure.dependencias import obtener_catalogo

enrutador_vocacional = APIRouter(prefix="/api/v1", tags=["Orientación vocacional"])


class EsquemaVocacional(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="forbid", allow_inf_nan=False
    )


class PreferenciasVocacionales(EsquemaVocacional):
    presupuesto_maximo: float | None = Field(None, ge=0, le=100000)
    duracion_maxima: int | None = Field(None, ge=1, le=240)
    modalidad_preferida: Literal["Presencial", "Semipresencial", "Virtual"] | None = None


class CapturaPreferencia(EsquemaVocacional):
    id_registro: UUID
    id_participante: UUID
    eleccion: str = Field(min_length=1, max_length=150)
    consentimiento: Literal[True]
    mayor_edad: Literal[True]


CadenaRespuesta = Annotated[str, StringConstraints(min_length=1, max_length=150)]


class SolicitudVocacional(EsquemaVocacional):
    ids_programas: list[CadenaRespuesta] = Field(min_length=2, max_length=2)
    version: str = Field(max_length=60)
    respuestas: dict[Annotated[str, StringConstraints(max_length=3)], CadenaRespuesta] = Field(
        min_length=10, max_length=10
    )
    preferencias: PreferenciasVocacionales = Field(default_factory=PreferenciasVocacionales)
    captura: CapturaPreferencia | None = None


class OpcionRespuesta(EsquemaVocacional):
    id: str
    texto: str


class PreguntaRespuesta(EsquemaVocacional):
    id: str
    texto: str
    seccion: str
    contexto: str = ""
    opciones: list[OpcionRespuesta]


class ProgramaRespuesta(EsquemaVocacional):
    id: str
    nombre: str
    institucion: str


class CuestionarioRespuesta(EsquemaVocacional):
    version: str
    preguntas: list[PreguntaRespuesta]
    programas: list[ProgramaRespuesta] = Field(default_factory=list)
    aviso: str = "Orientación comparativa; no es un instrumento psicológico validado."


class FactorRespuesta(EsquemaVocacional):
    factor: str
    descripcion: str
    valor: float
    contribucion: float


class RecomendacionRespuesta(EsquemaVocacional):
    estado: str
    explicacion: str
    programas: list[ProgramaRespuesta]
    version_cuestionario: str
    recomendada: str | None
    id_registro: str | None
    factores: list[FactorRespuesta]
    factores_contrarios: list[FactorRespuesta]
    incertidumbres: list[str]
    modelo: dict | None
    aviso: str
    margen: float | None = None


def presentar(valor):
    if isinstance(valor, dict):
        return {to_camel(k): presentar(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [presentar(v) for v in valor]
    return valor


def servicio(solicitud, catalogo):
    return RecomendarPreferencia(
        catalogo, solicitud.app.state.motor_preferencias, solicitud.app.state.registro_preferencias
    )


@enrutador_vocacional.get("/cuestionario", response_model=CuestionarioRespuesta)
def obtener_generales():
    return presentar(
        {"version": VERSION_CUESTIONARIO, "preguntas": [asdict(p) for p in preguntas_generales()]}
    )


@enrutador_vocacional.get("/cuestionario/comparativo", response_model=CuestionarioRespuesta)
def obtener_comparativo(
    solicitud: Request,
    ids_programas: list[str] = Query(min_length=2, max_length=2, alias="idsProgramas"),
    catalogo: Catalogo = Depends(obtener_catalogo),
):
    return presentar(servicio(solicitud, catalogo).preparar(ids_programas)[1])


@enrutador_vocacional.post("/recomendaciones", response_model=RecomendacionRespuesta)
def recomendar(
    cuerpo: SolicitudVocacional, solicitud: Request, catalogo: Catalogo = Depends(obtener_catalogo)
):
    try:
        resultado = servicio(solicitud, catalogo).ejecutar(
            cuerpo.ids_programas,
            cuerpo.respuestas,
            cuerpo.preferencias.model_dump(exclude_none=True),
            cuerpo.version,
            cuerpo.captura.model_dump(mode="json") if cuerpo.captura else None,
        )
        return presentar(resultado)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
