"""Composition root: the only place choosing concrete application adapters."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.adapters.input.http import router
from app.application.catalog import CareerNotFound
from app.infrastructure.database import session_factory
from app.infrastructure.settings import Settings

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None):
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app):
        yield
        if app.state.sessions:
            app.state.sessions.kw["bind"].dispose()

    app = FastAPI(title="ORIENTA API", version="0.5.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.sessions = session_factory(settings) if settings.data_mode == "postgres" else None
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET"],
        allow_headers=["Accept", "Content-Type"],
    )

    @app.exception_handler(CareerNotFound)
    async def not_found(request: Request, error: CareerNotFound):
        return JSONResponse(status_code=404, content={"detail": "Oferta no disponible"})

    @app.exception_handler(SQLAlchemyError)
    async def persistence_error(request: Request, error: SQLAlchemyError):
        # Do not log the exception message: it can contain connection credentials or query data.
        logger.error("Persistencia no disponible: %s", type(error).__name__)
        return JSONResponse(
            status_code=503,
            content={"detail": "No pudimos consultar el catálogo. Inténtalo nuevamente."},
        )

    app.include_router(router)
    return app


app = create_app()
