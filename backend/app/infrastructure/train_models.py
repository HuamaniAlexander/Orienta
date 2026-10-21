"""Compatibilidad con el comando histórico; usar app.infrastructure.entrenar_modelos."""

if __name__ == "__main__":
    import runpy

    runpy.run_module("app.infrastructure.entrenar_modelos", run_name="__main__")
