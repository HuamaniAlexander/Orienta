import json

import pytest

from app.infrastructure.recommendation_training import approved, features, prepare, train, validate


def test_blind_pilot_partitions_and_refuses_unreviewed_training(tmp_path):
    path = tmp_path / "pilot.json"
    prepare(__import__("pathlib").Path("data/catalog.json"), path)
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
