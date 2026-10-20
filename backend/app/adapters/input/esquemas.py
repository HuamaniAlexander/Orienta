from datetime import date
from decimal import Decimal

from pydantic import AliasChoices, AliasGenerator, BaseModel, ConfigDict, Field

from app.adapters.contratos import CAMPOS_EXTERNOS


class EsquemaContrato(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=AliasGenerator(
            validation_alias=lambda campo: AliasChoices(CAMPOS_EXTERNOS.get(campo, campo), campo),
            serialization_alias=lambda campo: CAMPOS_EXTERNOS.get(campo, campo),
        ),
    )


class RespuestaFuente(EsquemaContrato):
    model_config = ConfigDict(from_attributes=True)
    campo: str
    referencia: str | None
    estado: str


class RespuestaCarrera(EsquemaContrato):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nombre: str
    institucion: str
    tipo_formacion: str | None
    modalidad: str | None
    ubicacion: str | None
    duracion_meses: int | None
    costo_mensual_soles: Decimal | None
    requisitos: str | None
    campo_laboral: str | None
    fecha_revision: date | None
    fuentes: list[RespuestaFuente]
    detalles: dict = Field(default_factory=dict, exclude_if=lambda valor: not valor)


class RespuestaCatalogo(EsquemaContrato):
    elementos: list[RespuestaCarrera]
    total: int
    pagina: int
    limite: int
    modo_datos: str


class SolicitudComparacion(EsquemaContrato):
    model_config = ConfigDict(extra="forbid")
    ids_carreras: list[str] = Field(min_length=2, max_length=2)


class RespuestaComparacion(EsquemaContrato):
    model_config = ConfigDict(from_attributes=True)
    izquierda: RespuestaCarrera
    derecha: RespuestaCarrera
    diferencia_duracion_meses: int | None
    diferencia_costo_mensual_soles: Decimal | None


class PreferenciasRecomendacion(EsquemaContrato):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    presupuesto_soles: float | None = Field(default=None, ge=0)
    duracion_maxima_meses: int | None = Field(default=None, ge=1, le=240)
    modalidad: str | None = Field(default=None, max_length=100)
    ubicacion: str | None = Field(default=None, max_length=200)
    intereses_laborales: str | None = Field(default=None, max_length=500)
    requisitos_cumplidos: str | None = Field(default=None, max_length=500)


class SolicitudAnalisis(SolicitudComparacion):
    preferencias: PreferenciasRecomendacion = Field(default_factory=PreferenciasRecomendacion)


class RespuestaAnalisisCriterio(EsquemaContrato):
    etiqueta_aprendida: str | None = None
    motivo: str
    etiqueta_izquierda: str
    etiqueta_derecha: str
    clave: str
    etiqueta: str
    valor_izquierda: str
    valor_derecha: str
    relacion: str
    explicacion: str
    recomendacion: str
    advertencias: list[str]


class RespuestaAnalisis(EsquemaContrato):
    entrenamiento_recomendaciones: dict
    analisis_criterios: list[RespuestaAnalisisCriterio]
    tipo_explicacion: str
    umbral_calidad: float
    calidad_aprobada: bool
    evaluaciones_modelos: list[dict[str, str | float | None]]
    prediccion: str
    contraste_catalogo: str
    areas: list[str]
    fuentes_areas: list[str | None]
    coincide_catalogo: bool
    nombre_modelo: str
    version_modelo: str
    metricas: dict[str, float]
    exactitud_referencia: float
    pares_entrenamiento: int
    pares_prueba: int
    limitaciones: list[str]
    siguientes_pasos: list[str]
    recomendaciones: list[RespuestaCarrera]
