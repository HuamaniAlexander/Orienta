import json
from pathlib import Path

import pytest

from app.adapters.output.criterion_recommendations import ReviewedRecommendations
from app.domain.recommendation import CRITERIA, LABELS
from app.infrastructure.recommendation_training import approved, features, prepare, train, validate


def test_blind_pilot_partitions_and_refuses_unreviewed_training(tmp_path):
    path = tmp_path / "pilot.json"
    prepare(Path("data/catalog.json"), path)
    rows = json.loads(path.read_text(encoding="utf8"))
    offers = {
        s: {r[k] for r in rows if r["split"] == s for k in ("left_id", "right_id")}
        for s in ("train", "validation", "test")
    }
    assert not offers["train"] & offers["test"]
    assert not offers["train"] & offers["validation"]
    assert not offers["validation"] & offers["test"]
    assert all(r["label"] is None and not r["approved"] for r in rows)
    with pytest.raises(ValueError, match="revisores"):
        train(path, tmp_path / "models")
    assert not (tmp_path / "models").exists()
    with pytest.raises(ValueError, match="ya existe"):
        prepare(Path("data/catalog.json"), path)


def test_gate_is_per_metric_and_labels_are_not_predictors():
    scores = dict(accuracy=0.99, precision_macro=0.95, recall_macro=0.91, f1_macro=0.90)
    assert not approved(scores)
    assert approved(scores | {"f1_macro": 0.91})
    row = dict(
        criterion="cost",
        left_value="0",
        right_value=None,
        preferences={"budget": 1000},
        label="favor_left",
        reason="secret",
    )
    assert features(row) == features(row | {"label": "favor_right", "reason": "different"})
    assert features(row)["left_number"] == 0
    assert features(row)["right_missing"] == 1


def test_rejects_duplicate_pair_and_same_offer():
    with pytest.raises(ValueError, match="diferentes"):
        validate([dict(split="train", criterion="cost", left_id="X", right_id="X")])


def reviewed_fixture():
    # Test-only mechanical labels: never exported as a real recommendation corpus.
    rows = []
    for split in ("train", "validation", "test"):
        for index in range(25):
            for criterion in CRITERIA:
                label = LABELS[index % 5]
                rows.append(
                    dict(
                        split=split,
                        criterion=criterion,
                        left_id=f"{split}-{index}-left",
                        right_id=f"{split}-{index}-right",
                        left_value=60 if criterion in ("duration", "cost") else "same",
                        right_value=60 if criterion in ("duration", "cost") else "same",
                        preferences={"budget_pen": 1000},
                        label=label,
                        reason="Test fixture only",
                        evidence=["test fixture"],
                        reviewer_1="test reviewer one",
                        reviewer_2="test reviewer two",
                        reviewer_1_label=label,
                        reviewer_2_label=label,
                        approved=True,
                    )
                )
    return rows


def test_full_training_pipeline_and_independent_quality_gate(tmp_path):
    path = tmp_path / "test-only.json"
    path.write_text(json.dumps(reviewed_fixture()), encoding="utf8")
    report = train(path, tmp_path / "models")
    assert not report["quality_approved"]
    assert set(report["criteria"]) == set(CRITERIA)
    for criterion in report["criteria"].values():
        assert len(criterion["candidates"]) == 9
        assert sum(map(sum, criterion["test"]["confusion_matrix"])) == 25
    status, predictions = ReviewedRecommendations(tmp_path / "models").analyze(None, None, {})
    assert status["status"] == "below_quality_target"
    assert not predictions


def test_leakage_and_unresolved_disagreement_are_rejected():
    rows = reviewed_fixture()
    rows[-1]["left_id"] = rows[0]["left_id"]
    with pytest.raises(ValueError, match="Fuga"):
        validate(rows)
    rows = reviewed_fixture()
    rows[0]["reviewer_2_label"] = "insufficient_data"
    with pytest.raises(ValueError, match="desacuerdo"):
        validate(rows)
