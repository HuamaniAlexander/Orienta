"""Entrenamiento reproducible fuera del procesamiento de solicitudes HTTP."""

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

from app.adapters.output.caracteristicas_ia import (
    CATEGORICAS,
    NUMERICAS,
    caracteristicas,
    firma,
)
from app.adapters.output.repositorios_carreras import RepositorioCarrerasJson

RAIZ = Path(__file__).resolve().parents[2]


def formar_pares(carreras, metadatos):
    filas, etiquetas = [], []
    for a, b in combinations(carreras, 2):
        filas.append(caracteristicas(a, b))
        etiquetas.append(int(metadatos[a.id]["area"] != metadatos[b.id]["area"]))
    return pd.DataFrame(filas, columns=NUMERICAS + CATEGORICAS), np.array(etiquetas)


def metricas(y, predicho):
    precision, exhaustividad, f1, _ = precision_recall_fscore_support(
        y, predicho, labels=[0, 1], average="macro", zero_division=0
    )
    return dict(
        accuracy=float(accuracy_score(y, predicho)),
        precision_macro=float(precision),
        recall_macro=float(exhaustividad),
        f1_macro=float(f1),
        confusion_matrix=confusion_matrix(y, predicho, labels=[0, 1]).tolist(),
    )


PUNTUACIONES = ("accuracy", "precision_macro", "recall_macro", "f1_macro")


def distancia_al_ideal(puntuaciones):
    """Distancia RMS ponderada por igual al resultado ideal de validación; menor es mejor."""
    return float(np.sqrt(np.mean([(1 - puntuaciones[clave]) ** 2 for clave in PUNTUACIONES])))


def cumple_objetivo_calidad(puntuaciones, objetivo=0.90):
    return all(puntuaciones[clave] >= objetivo for clave in PUNTUACIONES)


def entrenar(catalogo: Path, ruta_metadatos: Path, salida: Path):
    carreras = RepositorioCarrerasJson(catalogo).carreras
    metadatos = json.loads(ruta_metadatos.read_text(encoding="utf-8"))
    if any(
        c.id not in metadatos or not metadatos[c.id]["area"] or not metadatos[c.id]["group"]
        for c in carreras
    ):
        raise ValueError("Faltan áreas o grupos documentados")
    grupos = np.array([metadatos[c.id]["group"] for c in carreras])
    separador_externo = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
    indices_entrenamiento, indices_prueba = next(separador_externo.split(carreras, groups=grupos))
    carreras_entrenamiento = [carreras[i] for i in indices_entrenamiento]
    carreras_prueba = [carreras[i] for i in indices_prueba]
    x_entrenamiento, y_entrenamiento = formar_pares(carreras_entrenamiento, metadatos)
    x_prueba, y_prueba = formar_pares(carreras_prueba, metadatos)
    if len(set(y_entrenamiento)) < 2 or not len(y_prueba):
        raise ValueError("Grupos insuficientes para entrenar y evaluar")
    preprocesador = ColumnTransformer(
        [
            (
                "numeric",
                Pipeline(
                    [("missing", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
                ),
                NUMERICAS,
            ),
            ("categories", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
        ]
    )
    modelos = {
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
    grupos_internos = [metadatos[c.id]["group"] for c in carreras_entrenamiento]
    particiones, informacion_particiones = [], []
    for a, b in GroupShuffleSplit(n_splits=12, test_size=0.35, random_state=43).split(
        carreras_entrenamiento, groups=grupos_internos
    ):
        ajuste = [carreras_entrenamiento[i] for i in a]
        validacion = [carreras_entrenamiento[i] for i in b]
        xf, yf = formar_pares(ajuste, metadatos)
        xv, yv = formar_pares(validacion, metadatos)
        if len(set(yf)) < 2 or not len(yv):
            continue
        particiones.append((xf, yf, xv, yv))
        informacion_particiones.append(
            {
                "train_groups": sorted({grupos_internos[i] for i in a}),
                "validation_groups": sorted({grupos_internos[i] for i in b}),
            }
        )
        if len(particiones) == 4:
            break
    if len(particiones) < 2:
        raise ValueError("No hay grupos suficientes para validación sin contaminación")
    ajustados, resultados = {}, {}
    for nombre, candidatos in modelos.items():
        puntuaciones_candidato = []
        for modelo in candidatos:
            canalizacion = Pipeline([("preprocess", preprocesador), ("model", modelo)])
            puntuaciones_particiones = [
                metricas(yv, clone(canalizacion).fit(xf, yf).predict(xv))
                for xf, yf, xv, yv in particiones
            ]
            validacion = {
                clave: float(np.mean([s[clave] for s in puntuaciones_particiones]))
                for clave in PUNTUACIONES
            }
            puntuaciones_candidato.append((distancia_al_ideal(validacion), validacion, modelo))
        distancia, validacion, modelo = min(
            puntuaciones_candidato, key=lambda candidato: candidato[0]
        )
        ajustados[nombre] = Pipeline(
            [("preprocess", clone(preprocesador)), ("model", clone(modelo))]
        ).fit(x_entrenamiento, y_entrenamiento)
        resultados[nombre] = metricas(y_prueba, ajustados[nombre].predict(x_prueba)) | {
            "validation_scores": validacion,
            "validation_distance_to_ideal": distancia,
            "validation_f1_macro": validacion["f1_macro"],
            "selected_parameters": modelo.get_params(),
            "candidates_evaluated": len(candidatos),
        }
    seleccionado = min(
        resultados, key=lambda nombre: resultados[nombre]["validation_distance_to_ideal"]
    )
    referencia_base = DummyClassifier(strategy="most_frequent").fit(
        x_entrenamiento, y_entrenamiento
    )
    vectorizador = TfidfVectorizer(strip_accents="unicode", ngram_range=(1, 2), min_df=1)
    textos = [f"{c.nombre} {c.campo_laboral or ''} {c.requisitos or ''}" for c in carreras]
    matriz = vectorizador.fit_transform(textos)
    salida.mkdir(parents=True, exist_ok=True)
    artefacto = salida / "modelo.joblib"
    joblib.dump(
        {
            "classifier": ajustados[seleccionado],
            "vectorizer": vectorizador,
            "content_matrix": matriz,
            "ids": [c.id for c in carreras],
        },
        artefacto,
        compress=3,
    )
    informe = {
        "version": "1.2.0",
        "seed": 42,
        "sklearn_version": sklearn.__version__,
        "catalog_sha256": sha256(catalogo.read_bytes()).hexdigest(),
        "artifact_sha256": sha256(artefacto.read_bytes()).hexdigest(),
        "selected_model": seleccionado,
        "selection_criterion": "minimum_validation_distance_to_ideal",
        "quality_target": 0.90,
        "quality_approved": cumple_objetivo_calidad(resultados[seleccionado]),
        "training_offers": len(carreras_entrenamiento),
        "test_offers": len(carreras_prueba),
        "training_pairs": len(y_entrenamiento),
        "test_pairs": len(y_prueba),
        "train_groups": sorted(set(grupos[indices_entrenamiento])),
        "test_groups": sorted(set(grupos[indices_prueba])),
        "validation_splits": informacion_particiones,
        "models": resultados,
        "baseline": metricas(y_prueba, referencia_base.predict(x_prueba)),
        "metadata": {c.id: metadatos[c.id] | {"signature": firma(c)} for c in carreras},
        "limitations": [
            f"{len(carreras)} ofertas de {len({c.institucion for c in carreras})} instituciones; "
            "muestra pequeña y sin validación vocacional.",
            "Costo, duración y modalidad no describen suficientemente el área académica.",
            "Los costos estimados no son tarifas oficiales ni costos totales.",
            "La similitud de contenido no mide aptitudes, preferencias ni empleabilidad.",
        ],
    }
    (salida / "metricas.json").write_text(
        json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                k: informe[k]
                for k in ["selected_model", "training_pairs", "test_pairs", "models", "baseline"]
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return informe


if __name__ == "__main__":
    argumentos_cli = argparse.ArgumentParser(
        description="Entrenar contraste académico fuera de HTTP"
    )
    argumentos_cli.add_argument(
        "--catalogo", "--catalog", dest="catalogo", type=Path, default=RAIZ / "data/catalogo.json"
    )
    argumentos_cli.add_argument(
        "--metadatos", "--metadata", dest="metadatos", type=Path, default=RAIZ / "data/areas.json"
    )
    argumentos_cli.add_argument(
        "--salida", "--output", dest="salida", type=Path, default=RAIZ / "models"
    )
    argumentos = argumentos_cli.parse_args()
    entrenar(argumentos.catalogo, argumentos.metadatos, argumentos.salida)
