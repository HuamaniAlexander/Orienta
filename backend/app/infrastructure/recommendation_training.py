"""Human-reviewed recommendation experiment; never manufacture training labels.

Run --prepare to create a blind annotation pilot, then --train after review.
No model is released unless ALL criteria pass the independent test gate.
"""

import argparse
import json
from hashlib import sha256
from itertools import combinations
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.pipeline import make_pipeline
from sklearn.tree import DecisionTreeClassifier

from app.domain.recommendation import CRITERIA, LABELS, approved, features

ROOT = Path(__file__).resolve().parents[2]


def prepare(catalog, output):
    if output.exists():
        raise ValueError("La salida ya existe; elige otra ruta para conservar las anotaciones")
    offers = json.loads(catalog.read_text(encoding="utf8"))
    # Partition OFFERS before forming pairs: no shared offer across any split.
    rng = np.random.default_rng(42)
    rng.shuffle(offers)
    cut1, cut2 = int(len(offers) * 0.6), int(len(offers) * 0.8)
    rows = []
    fields = dict(
        zip(
            CRITERIA,
            (
                "duration_months",
                "modality",
                "location",
                "monthly_cost_pen",
                "requirements",
                "employment",
            ),
        )
    )
    for split, pool in (
        ("train", offers[:cut1]),
        ("validation", offers[cut1:cut2]),
        ("test", offers[cut2:]),
    ):
        pairs = list(combinations(pool, 2))
        rng.shuffle(pairs)
        for left, right in pairs[: {"train": 60, "validation": 20, "test": 20}[split]]:
            for criterion in CRITERIA:
                rows.append(
                    dict(
                        comparison_id=f"{left['id']}:{right['id']}",
                        split=split,
                        criterion=criterion,
                        left_id=left["id"],
                        right_id=right["id"],
                        left_name=f"{left['name']} · {left['institution']}",
                        right_name=f"{right['name']} · {right['institution']}",
                        left_value=left[fields[criterion]],
                        right_value=right[fields[criterion]],
                        preferences={},
                        evidence=left["sources"] + right["sources"],
                        label=None,
                        reason=None,
                        reviewer_1=None,
                        reviewer_2=None,
                        reviewer_1_label=None,
                        reviewer_2_label=None,
                        adjudication=None,
                        approved=False,
                    )
                )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf8")
    return len(rows)


def validate(rows):
    if not rows:
        raise ValueError("No hay ejemplos revisados")
    offers = {s: set() for s in ("train", "validation", "test")}
    seen = set()
    for row in rows:
        if row["split"] not in offers or row["criterion"] not in CRITERIA:
            raise ValueError("Partición o criterio inválido")
        if row["left_id"] == row["right_id"]:
            raise ValueError("Una comparación requiere ofertas diferentes")
        key = (tuple(sorted((row["left_id"], row["right_id"]))), row["criterion"])
        if key in seen:
            raise ValueError("Comparación duplicada o invertida")
        seen.add(key)
        offers[row["split"]].update((row["left_id"], row["right_id"]))
        if (
            row.get("approved") is not True
            or row.get("label") not in LABELS
            or not row.get("reason")
            or not row.get("evidence")
            or not row.get("reviewer_1")
            or not row.get("reviewer_2")
            or row["reviewer_1"] == row["reviewer_2"]
            or row.get("reviewer_1_label") not in LABELS
            or row.get("reviewer_2_label") not in LABELS
        ):
            raise ValueError("Cada etiqueta exige evidencia y dos revisores distintos")
        if (
            row["reviewer_1_label"] != row["reviewer_2_label"]
            or row["label"] != row["reviewer_1_label"]
        ) and not row.get("adjudication"):
            raise ValueError("El desacuerdo requiere resolución documentada")
    for a, b in combinations(offers, 2):
        if offers[a] & offers[b]:
            raise ValueError("Fuga: una oferta aparece en varias particiones")
    for criterion in CRITERIA:
        for split in offers:
            labels = [
                r["label"] for r in rows if r["criterion"] == criterion and r["split"] == split
            ]
            if any(labels.count(label) < 5 for label in LABELS):
                raise ValueError(f"{criterion}/{split}: mínimo 5 ejemplos por clase")


def measure(actual, predicted):
    p, r, f, _ = precision_recall_fscore_support(
        actual, predicted, labels=LABELS, average="macro", zero_division=0
    )
    return dict(
        accuracy=float(accuracy_score(actual, predicted)),
        precision_macro=float(p),
        recall_macro=float(r),
        f1_macro=float(f),
        confusion_matrix=confusion_matrix(actual, predicted, labels=LABELS).tolist(),
    )


def train(dataset, output):
    rows = json.loads(dataset.read_text(encoding="utf8"))
    validate(rows)  # Refuse unreviewed data before fitting or writing artifacts.
    models, reports = {}, {}
    for criterion in CRITERIA:
        splits = {
            s: [r for r in rows if r["criterion"] == criterion and r["split"] == s]
            for s in ("train", "validation", "test")
        }
        candidates = []
        for depth in (3, 8, None):
            for name, estimator in (
                (
                    "decision_tree",
                    DecisionTreeClassifier(
                        max_depth=depth, class_weight="balanced", random_state=42
                    ),
                ),
                (
                    "random_forest",
                    RandomForestClassifier(
                        n_estimators=150, max_depth=depth, class_weight="balanced", random_state=42
                    ),
                ),
                (
                    "logistic_regression",
                    LogisticRegression(
                        C={3: 0.1, 8: 1, None: 10}[depth], class_weight="balanced", max_iter=3000
                    ),
                ),
            ):
                model = make_pipeline(DictVectorizer(), estimator)
                model.fit(
                    [features(r) for r in splits["train"]], [r["label"] for r in splits["train"]]
                )
                scores = measure(
                    [r["label"] for r in splits["validation"]],
                    model.predict([features(r) for r in splits["validation"]]),
                )
                distance = float(
                    np.sqrt(
                        np.mean(
                            [
                                (1 - scores[k]) ** 2
                                for k in ("accuracy", "precision_macro", "recall_macro", "f1_macro")
                            ]
                        )
                    )
                )
                candidates.append((distance, name, model, scores))
        _, name, winner, validation = min(candidates, key=lambda c: c[0])
        test = measure(
            [r["label"] for r in splits["test"]],
            winner.predict([features(r) for r in splits["test"]]),
        )
        models[criterion] = winner
        reports[criterion] = dict(
            selected=name,
            validation=validation,
            test=test,
            approved=approved(test),
            candidates=[dict(name=c[1], distance=c[0], validation=c[3]) for c in candidates],
            samples={s: len(v) for s, v in splits.items()},
        )
    report = dict(
        dataset_sha256=sha256(dataset.read_bytes()).hexdigest(),
        quality_target=0.90,
        quality_approved=all(r["approved"] for r in reports.values()),
        labels=LABELS,
        criteria=reports,
        status="evaluated",
    )
    output.mkdir(parents=True, exist_ok=True)
    # Experimental artifact stays distinct from the area classifier and is never auto-deployed.
    joblib.dump(models, output / "recommendations.joblib")
    report["artifact_sha256"] = sha256((output / "recommendations.joblib").read_bytes()).hexdigest()
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--catalog", type=Path, default=ROOT / "data/catalog.json")
    parser.add_argument("--dataset", type=Path, default=ROOT / "data/recommendations/pilot.json")
    parser.add_argument("--output", type=Path, default=ROOT / "models/recommendations")
    args = parser.parse_args()
    try:
        print(
            prepare(args.catalog, args.dataset)
            if args.prepare
            else train(args.dataset, args.output)
        )
    except ValueError as error:
        parser.exit(2, f"Entrenamiento pendiente: {error}\n")
