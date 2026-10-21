"""Compatibilidad con el comando histórico; usar app.infrastructure.entrenar_recomendaciones."""

if __name__ == "__main__":
    import runpy

    runpy.run_module("app.infrastructure.entrenar_recomendaciones", run_name="__main__")
