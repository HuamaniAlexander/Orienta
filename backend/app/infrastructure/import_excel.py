"""Compatibilidad con el comando histórico; usar app.infrastructure.importar_excel."""

if __name__ == "__main__":
    import runpy

    runpy.run_module("app.infrastructure.importar_excel", run_name="__main__")
