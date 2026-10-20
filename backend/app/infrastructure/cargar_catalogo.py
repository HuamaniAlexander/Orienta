"""Cargar el catálogo versionado en PostgreSQL sin depender de archivos externos."""

from hashlib import sha256
from pathlib import Path

from app.adapters.output.importador import importar_carreras
from app.adapters.output.repositorios_carreras import RepositorioCarrerasJson
from app.infrastructure.base_datos import crear_sesiones
from app.infrastructure.configuracion import Configuracion


def principal():
    configuracion = Configuracion()
    ruta = Path(__file__).resolve().parents[2] / "data/catalogo.json"
    carreras = RepositorioCarrerasJson(ruta).carreras
    with crear_sesiones(configuracion)() as sesion:
        print(importar_carreras(carreras, sha256(ruta.read_bytes()).hexdigest(), ruta.name, sesion))


if __name__ == "__main__":
    principal()
