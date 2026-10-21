import json
from dataclasses import replace
from pathlib import Path

import joblib
import pytest
from fastapi.testclient import TestClient

from app.adapters.output.analisis_entrenado import AnalisisEntrenado
from app.adapters.output.caracteristicas_ia import caracteristicas
from app.adapters.output.repositorios_carreras import RepositorioCarrerasJson
from app.infrastructure.configuracion import Configuracion
from app.infrastructure.entrenar_modelos import formar_pares, metricas
from app.infrastructure.principal import crear_aplicacion
from app.ports.motor_analisis import AnalisisNoDisponible


def test_grupos_metricas_y_prediccion_simetrica():
    informe = json.loads(Path("models/metricas.json").read_text(encoding="utf-8"))
    assert not set(informe["train_groups"]) & set(informe["test_groups"])
    for particion in informe["validation_splits"]:
        assert not set(particion["train_groups"]) & set(particion["validation_groups"])
        assert not (set(particion["train_groups"]) | set(particion["validation_groups"])) & set(
            informe["test_groups"]
        )
    for modelo in informe["models"].values():
        assert sum(sum(fila) for fila in modelo["confusion_matrix"]) == informe["test_pairs"]
    repo = RepositorioCarrerasJson(Path("data/catalogo.json"))
    izquierda, derecha = repo.obtener("C01"), repo.obtener("C02")
    assert caracteristicas(izquierda, derecha) == caracteristicas(derecha, izquierda)
    servicio = AnalisisEntrenado(Path("models"))
    resultado, invertido = (
        servicio.analizar(izquierda, derecha),
        servicio.analizar(derecha, izquierda),
    )
    assert resultado["prediction"] == invertido["prediction"]
    assert resultado["catalog_contrast"] == "Áreas distintas"
    assert not {"C01", "C02"} & set(resultado["related_ids"])
    assert (
        resultado["metrics"]["accuracy"] == informe["models"][informe["selected_model"]]["accuracy"]
    )
    reservadas = [
        c for c in repo.carreras if informe["metadata"][c.id]["group"] in informe["test_groups"]
    ]
    x, y = formar_pares(reservadas, informe["metadata"])
    artefacto = joblib.load("models/modelo.joblib")
    medido = metricas(y, artefacto["classifier"].predict(x))
    assert medido["accuracy"] == informe["models"][informe["selected_model"]]["accuracy"]
    assert (
        medido["confusion_matrix"]
        == informe["models"][informe["selected_model"]]["confusion_matrix"]
    )
    with pytest.raises(AnalisisNoDisponible):
        servicio.analizar(replace(izquierda, duracion_meses=61), derecha)


def test_analisis_http_y_fallo_conserva_comparacion(tmp_path):
    app = crear_aplicacion(
        Configuracion(modo_datos="demo", ruta_catalogo_json=Path("data/catalogo.json"))
    )
    with TestClient(app) as cliente:
        respuesta = cliente.post("/api/comparaciones/analisis", json={"career_ids": ["C01", "C02"]})
        assert respuesta.status_code == 200, respuesta.text
        cuerpo = respuesta.json()
        assert len(cuerpo["recommendations"]) == 3
        assert not {"C01", "C02"} & {c["id"] for c in cuerpo["recommendations"]}
        assert len(cuerpo["area_sources"]) == 2
        assert len(cuerpo["criteria_analysis"]) == 6
        assert len(cuerpo["next_steps"]) == 6
        assert len(cuerpo["model_evaluations"]) == 3
        assert cuerpo["quality_target"] == 0.90
        assert cuerpo["recommendation_training"]["status"] == "awaiting_reviewed_labels"
        assert all(
            elemento["reason"] and "Universidad" in elemento["left_label"]
            for elemento in cuerpo["criteria_analysis"]
        )
        assert (
            cliente.post(
                "/api/comparaciones/analisis",
                json={"career_ids": ["C01", "C02"], "preferences": {"budget_pen": -1}},
            ).status_code
            == 422
        )
        app.state.servicio_analisis = AnalisisEntrenado(tmp_path)
        assert (
            cliente.post(
                "/api/comparaciones/analisis", json={"career_ids": ["C01", "C02"]}
            ).status_code
            == 503
        )
        assert (
            cliente.post("/api/comparaciones", json={"career_ids": ["C01", "C02"]}).status_code
            == 200
        )


def test_catalogo_ampliado_analizable_sin_afirmar_calidad():
    with TestClient(
        crear_aplicacion(
            Configuracion(modo_datos="demo", ruta_catalogo_json=Path("data/catalogo.json"))
        )
    ) as cliente:
        for code in range(20, 36):
            respuesta = cliente.post(
                "/api/comparaciones/analisis",
                json={"career_ids": ["C01", f"C{code}"], "preferences": {"budget_pen": 1000}},
            )
            assert respuesta.status_code == 200, respuesta.text
            assert not respuesta.json()["recommendation_training"]["quality_approved"]
            assert len(respuesta.json()["criteria_analysis"]) == 6
