"""Offline reproducible training. Never imported by the HTTP request path."""

import argparse
import json
from hashlib import sha256
from itertools import combinations
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from app.adapters.output.ml_features import CATEGORICAL, NUMERIC, features, signature
from app.adapters.output.repositories import JsonCareerRepository

ROOT = Path(__file__).resolve().parents[2]


def pairs(careers, metadata):
    rows, labels = [], []
    for a, b in combinations(careers, 2):
        rows.append(features(a, b))
        labels.append(int(metadata[a.id]["area"] != metadata[b.id]["area"]))
    return pd.DataFrame(rows, columns=NUMERIC + CATEGORICAL), np.array(labels)


def metrics(y, predicted):
    precision, recall, f1, _ = precision_recall_fscore_support(
        y, predicted, labels=[0, 1], average="macro", zero_division=0
    )
    return dict(
        accuracy=float(accuracy_score(y, predicted)),
        precision_macro=float(precision),
        recall_macro=float(recall),
        f1_macro=float(f1),
        confusion_matrix=confusion_matrix(y, predicted, labels=[0, 1]).tolist(),
    )


SCORES = ("accuracy", "precision_macro", "recall_macro", "f1_macro")


def distance_to_ideal(scores):
    """Equal-weight RMS distance to perfect validation scores; smaller is better."""
    return float(np.sqrt(np.mean([(1 - scores[key]) ** 2 for key in SCORES])))


def meets_quality_target(scores, target=0.90):
    return all(scores[key] >= target for key in SCORES)


def train(catalog: Path, metadata_path: Path, output: Path):
    careers = JsonCareerRepository(catalog).careers
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if any(
        c.id not in metadata or not metadata[c.id]["area"] or not metadata[c.id]["group"]
        for c in careers
    ):
        raise ValueError("Faltan áreas o grupos documentados")
    groups = np.array([metadata[c.id]["group"] for c in careers])
    outer = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
    train_indices, test_indices = next(outer.split(careers, groups=groups))
    train_careers = [careers[i] for i in train_indices]
    test_careers = [careers[i] for i in test_indices]
    x_train, y_train = pairs(train_careers, metadata)
    x_test, y_test = pairs(test_careers, metadata)
    if len(set(y_train)) < 2 or not len(y_test):
        raise ValueError("Grupos insuficientes para entrenar y evaluar")
    preprocess = ColumnTransformer(
        [
            (
                "numeric",
                Pipeline(
                    [("missing", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
                ),
                NUMERIC,
            ),
            ("categories", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
        ]
    )
    models = {
        "Árbol de decisión": [
            DecisionTreeClassifier(max_depth=d, class_weight=w, random_state=42)
            for d in (2, 4, None)
            for w in (None, "balanced")
        ],
        "Random Forest": [
            RandomForestClassifier(
                n_estimators=100, max_depth=d, class_weight=w, random_state=42, n_jobs=1
            )
            for d in (2, 4, None)
            for w in (None, "balanced")
        ],
        "Regresión logística": [
            LogisticRegression(C=c, class_weight=w, max_iter=2000, random_state=42)
            for c in (0.1, 1, 10)
            for w in (None, "balanced")
        ],
    }
    inner_groups = [metadata[c.id]["group"] for c in train_careers]
    splits, split_info = [], []
    for a, b in GroupShuffleSplit(n_splits=12, test_size=0.35, random_state=43).split(
        train_careers, groups=inner_groups
    ):
        fit = [train_careers[i] for i in a]
        validation = [train_careers[i] for i in b]
        xf, yf = pairs(fit, metadata)
        xv, yv = pairs(validation, metadata)
        if len(set(yf)) < 2 or not len(yv):
            continue
        splits.append((xf, yf, xv, yv))
        split_info.append(
            {
                "train_groups": sorted({inner_groups[i] for i in a}),
                "validation_groups": sorted({inner_groups[i] for i in b}),
            }
        )
        if len(splits) == 4:
            break
    if len(splits) < 2:
        raise ValueError("No hay grupos suficientes para validación sin contaminación")
    fitted, results = {}, {}
    for name, candidates in models.items():
        candidate_scores = []
        for model in candidates:
            pipeline = Pipeline([("preprocess", preprocess), ("model", model)])
            fold_scores = [
                metrics(yv, clone(pipeline).fit(xf, yf).predict(xv)) for xf, yf, xv, yv in splits
            ]
            validation = {key: float(np.mean([s[key] for s in fold_scores])) for key in SCORES}
            candidate_scores.append((distance_to_ideal(validation), validation, model))
        distance, validation, model = min(candidate_scores, key=lambda candidate: candidate[0])
        fitted[name] = Pipeline([("preprocess", clone(preprocess)), ("model", clone(model))]).fit(
            x_train, y_train
        )
        results[name] = metrics(y_test, fitted[name].predict(x_test)) | {
            "validation_scores": validation,
            "validation_distance_to_ideal": distance,
            "validation_f1_macro": validation["f1_macro"],
            "selected_parameters": model.get_params(),
            "candidates_evaluated": len(candidates),
        }
    selected = min(results, key=lambda name: results[name]["validation_distance_to_ideal"])
    baseline = DummyClassifier(strategy="most_frequent").fit(x_train, y_train)
    vectorizer = TfidfVectorizer(strip_accents="unicode", ngram_range=(1, 2), min_df=1)
    texts = [f"{c.name} {c.employment or ''} {c.requirements or ''}" for c in careers]
    matrix = vectorizer.fit_transform(texts)
    output.mkdir(parents=True, exist_ok=True)
    artifact = output / "model.joblib"
    joblib.dump(
        {
            "classifier": fitted[selected],
            "vectorizer": vectorizer,
            "content_matrix": matrix,
            "ids": [c.id for c in careers],
        },
        artifact,
        compress=3,
    )
    report = {
        "version": "1.2.0",
        "seed": 42,
        "sklearn_version": sklearn.__version__,
        "catalog_sha256": sha256(catalog.read_bytes()).hexdigest(),
        "artifact_sha256": sha256(artifact.read_bytes()).hexdigest(),
        "selected_model": selected,
        "selection_criterion": "minimum_validation_distance_to_ideal",
        "quality_target": 0.90,
        "quality_approved": meets_quality_target(results[selected]),
        "training_offers": len(train_careers),
        "test_offers": len(test_careers),
        "training_pairs": len(y_train),
        "test_pairs": len(y_test),
        "train_groups": sorted(set(groups[train_indices])),
        "test_groups": sorted(set(groups[test_indices])),
        "validation_splits": split_info,
        "models": results,
        "baseline": metrics(y_test, baseline.predict(x_test)),
        "metadata": {c.id: metadata[c.id] | {"signature": signature(c)} for c in careers},
        "limitations": [
            f"{len(careers)} ofertas de {len({c.institution for c in careers})} instituciones; "
            "muestra pequeña y sin validación vocacional.",
            "Costo, duración y modalidad no describen suficientemente el área académica.",
            "Los costos estimados no son tarifas oficiales ni costos totales.",
            "La similitud de contenido no mide aptitudes, preferencias ni empleabilidad.",
        ],
    }
    (output / "metrics.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                k: report[k]
                for k in ["selected_model", "training_pairs", "test_pairs", "models", "baseline"]
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrenar contraste académico fuera de HTTP")
    parser.add_argument("--catalog", type=Path, default=ROOT / "data/catalog.json")
    parser.add_argument("--metadata", type=Path, default=ROOT / "data/areas.json")
    parser.add_argument("--output", type=Path, default=ROOT / "models")
    args = parser.parse_args()
    train(args.catalog, args.metadata, args.output)
