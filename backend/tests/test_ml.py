import json
from dataclasses import replace
from pathlib import Path

import joblib
import pytest
from fastapi.testclient import TestClient

from app.adapters.output.ml_analysis import TrainedAnalysis
from app.adapters.output.ml_features import features
from app.adapters.output.repositories import JsonCareerRepository
from app.infrastructure.main import create_app
from app.infrastructure.settings import Settings
from app.infrastructure.train_models import metrics, pairs
from app.ports.analysis import AnalysisUnavailable


def test_groups_metrics_and_symmetric_prediction():
    report = json.loads(Path("models/metrics.json").read_text(encoding="utf-8"))
    assert not set(report["train_groups"]) & set(report["test_groups"])
    for split in report["validation_splits"]:
        assert not set(split["train_groups"]) & set(split["validation_groups"])
        assert not (set(split["train_groups"]) | set(split["validation_groups"])) & set(
            report["test_groups"]
        )
    for model in report["models"].values():
        assert sum(sum(row) for row in model["confusion_matrix"]) == report["test_pairs"]
    repo = JsonCareerRepository(Path("data/catalog.json"))
    left, right = repo.get("C01"), repo.get("C02")
    assert features(left, right) == features(right, left)
    service = TrainedAnalysis(Path("models"))
    result, swapped = service.analyze(left, right), service.analyze(right, left)
    assert result["prediction"] == swapped["prediction"]
    assert result["catalog_contrast"] == "Áreas distintas"
    assert not {"C01", "C02"} & set(result["related_ids"])
    assert result["metrics"]["accuracy"] == report["models"][report["selected_model"]]["accuracy"]
    heldout = [
        c for c in repo.careers if report["metadata"][c.id]["group"] in report["test_groups"]
    ]
    x, y = pairs(heldout, report["metadata"])
    artifact = joblib.load("models/model.joblib")
    measured = metrics(y, artifact["classifier"].predict(x))
    assert measured["accuracy"] == report["models"][report["selected_model"]]["accuracy"]
    assert (
        measured["confusion_matrix"]
        == report["models"][report["selected_model"]]["confusion_matrix"]
    )
    with pytest.raises(AnalysisUnavailable):
        service.analyze(replace(left, duration_months=61), right)


def test_analysis_http_and_unavailable_keeps_comparison(tmp_path):
    app = create_app(Settings(data_mode="demo"))
    with TestClient(app) as client:
        response = client.post("/api/comparaciones/analisis", json={"career_ids": ["C01", "C02"]})
        assert response.status_code == 200, response.text
        body = response.json()
        assert len(body["recommendations"]) == 3
        assert not {"C01", "C02"} & {c["id"] for c in body["recommendations"]}
        assert len(body["area_sources"]) == 2
        app.state.analysis_service = TrainedAnalysis(tmp_path)
        assert (
            client.post(
                "/api/comparaciones/analisis", json={"career_ids": ["C01", "C02"]}
            ).status_code
            == 503
        )
        assert (
            client.post("/api/comparaciones", json={"career_ids": ["C01", "C02"]}).status_code
            == 200
        )
