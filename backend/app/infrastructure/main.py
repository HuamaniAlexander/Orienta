"""Entrada histórica de Uvicorn; la implementación usa nombres en español."""

from app.infrastructure.principal import app, crear_aplicacion

create_app = crear_aplicacion
__all__ = ["app", "create_app"]
