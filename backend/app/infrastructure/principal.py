"""Raíz de composición que selecciona los adaptadores concretos de la aplicación."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.adapters.input.http import enrutador
from app.adapters.input.vocacional import enrutador_vocacional
from app.adapters.output.analisis_entrenado import AnalisisEntrenado
from app.adapters.output.motor_preferencias import MotorPreferenciasLocal
from app.adapters.output.recomendaciones_criterios import RecomendacionesRevisadas
from app.adapters.output.registro_preferencias import RegistroPreferenciasSql
from app.application.catalogo import CarreraNoEncontrada
from app.domain.comparacion import ComparacionInvalida
from app.infrastructure.base_datos import crear_sesiones
from app.infrastructure.configuracion import Configuracion
from app.ports.motor_analisis import AnalisisNoDisponible

registro_eventos = logging.getLogger(__name__)


def crear_aplicacion(configuracion: Configuracion | None = None):
    configuracion = configuracion or Configuracion()

    @asynccontextmanager
    async def ciclo_vida(app):
        yield
        if app.state.sesiones:
            app.state.sesiones.kw["bind"].dispose()

    app = FastAPI(title="ORIENTA API", version="0.5.0", lifespan=ciclo_vida)
    app.state.configuracion = configuracion
    app.state.servicio_analisis = AnalisisEntrenado(configuracion.directorio_modelos)
    app.state.servicio_recomendaciones = RecomendacionesRevisadas(
        configuracion.directorio_modelos / "recomendaciones"
    )
    app.state.sesiones = (
        crear_sesiones(configuracion) if configuracion.modo_datos == "postgres" else None
    )
    app.state.motor_preferencias = MotorPreferenciasLocal(
        configuracion.directorio_modelos / "preferencias"
    )
    app.state.registro_preferencias = (
        RegistroPreferenciasSql(app.state.sesiones) if app.state.sesiones else None
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=configuracion.origenes_cors,
        allow_methods=["GET", "POST"],
        allow_headers=["Accept", "Content-Type"],
    )

    @app.exception_handler(ComparacionInvalida)
    async def comparacion_invalida(solicitud: Request, error: ComparacionInvalida):
        return JSONResponse(status_code=422, content={"detail": str(error)})

    @app.exception_handler(AnalisisNoDisponible)
    async def analisis_no_disponible(solicitud: Request, error: AnalisisNoDisponible):
        return JSONResponse(status_code=503, content={"detail": str(error)})

    @app.exception_handler(CarreraNoEncontrada)
    async def no_encontrada(solicitud: Request, error: CarreraNoEncontrada):
        return JSONResponse(status_code=404, content={"detail": "Oferta no disponible"})

    @app.exception_handler(SQLAlchemyError)
    async def error_persistencia(solicitud: Request, error: SQLAlchemyError):
        # El mensaje de excepción puede contener credenciales: registrar solo su tipo.
        registro_eventos.error("Persistencia no disponible: %s", type(error).__name__)
        return JSONResponse(
            status_code=503,
            content={"detail": "No pudimos consultar el catálogo. Inténtalo nuevamente."},
        )

    app.include_router(enrutador)
    app.include_router(enrutador_vocacional)
    return app


app = crear_aplicacion()
