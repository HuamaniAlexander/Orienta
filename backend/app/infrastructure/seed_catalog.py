"""Compatibilidad con el comando histórico; usar app.infrastructure.cargar_catalogo."""

if __name__ == "__main__":
    import runpy

    runpy.run_module("app.infrastructure.cargar_catalogo", run_name="__main__")
