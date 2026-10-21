"""Experimento de recomendaciones con etiquetas revisadas por personas.

Ejecutar --prepare para preparar el piloto y entrenar tras completar la revisión.
Todos los criterios deben superar la evaluación independiente para aprobar el modelo.
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

from app.domain.recomendacion import CRITERIOS, ETIQUETAS, caracteristicas, cumple_umbral

RAIZ = Path(__file__).resolve().parents[2]


def preparar(catalogo, salida):
    if salida.exists():
        raise ValueError("La salida ya existe; elige otra ruta para conservar las anotaciones")
    ofertas = json.loads(catalogo.read_text(encoding="utf8"))
    # Separar ofertas antes de formar pares para evitar compartirlas entre particiones.
    generador = np.random.default_rng(42)
    generador.shuffle(ofertas)
    corte_uno, corte_dos = int(len(ofertas) * 0.6), int(len(ofertas) * 0.8)
    filas = []
    campos = dict(
        zip(
            CRITERIOS,
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
    for particion, grupo_ofertas in (
        ("train", ofertas[:corte_uno]),
        ("validation", ofertas[corte_uno:corte_dos]),
        ("test", ofertas[corte_dos:]),
    ):
        formar_pares = list(combinations(grupo_ofertas, 2))
        generador.shuffle(formar_pares)
        for izquierda, derecha in formar_pares[
            : {"train": 60, "validation": 20, "test": 20}[particion]
        ]:
            for criterio in CRITERIOS:
                filas.append(
                    dict(
                        comparison_id=f"{izquierda['id']}:{derecha['id']}",
                        split=particion,
                        criterion=criterio,
                        left_id=izquierda["id"],
                        right_id=derecha["id"],
                        left_name=f"{izquierda['name']} · {izquierda['institution']}",
                        right_name=f"{derecha['name']} · {derecha['institution']}",
                        left_value=izquierda[campos[criterio]],
                        right_value=derecha[campos[criterio]],
                        preferences={},
                        evidence=izquierda["sources"] + derecha["sources"],
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
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(filas, ensure_ascii=False, indent=2), encoding="utf8")
    return len(filas)


def validar(filas):
    if not filas:
        raise ValueError("No hay ejemplos revisados")
    ofertas = {s: set() for s in ("train", "validation", "test")}
    vistos = set()
    for fila in filas:
        if fila["split"] not in ofertas or fila["criterion"] not in CRITERIOS:
            raise ValueError("Partición o criterio inválido")
        if fila["left_id"] == fila["right_id"]:
            raise ValueError("Una comparación requiere ofertas diferentes")
        clave = (tuple(sorted((fila["left_id"], fila["right_id"]))), fila["criterion"])
        if clave in vistos:
            raise ValueError("Comparación duplicada o invertida")
        vistos.add(clave)
        ofertas[fila["split"]].update((fila["left_id"], fila["right_id"]))
        if (
            fila.get("approved") is not True
            or fila.get("label") not in ETIQUETAS
            or not fila.get("reason")
            or not fila.get("evidence")
            or not fila.get("reviewer_1")
            or not fila.get("reviewer_2")
            or fila["reviewer_1"] == fila["reviewer_2"]
            or fila.get("reviewer_1_label") not in ETIQUETAS
            or fila.get("reviewer_2_label") not in ETIQUETAS
        ):
            raise ValueError("Cada etiqueta exige evidencia y dos revisores distintos")
        if (
            fila["reviewer_1_label"] != fila["reviewer_2_label"]
            or fila["label"] != fila["reviewer_1_label"]
        ) and not fila.get("adjudication"):
            raise ValueError("El desacuerdo requiere resolución documentada")
    for a, b in combinations(ofertas, 2):
        if ofertas[a] & ofertas[b]:
            raise ValueError("Fuga: una oferta aparece en varias particiones")
    for criterio in CRITERIOS:
        for particion in ofertas:
            etiquetas = [
                r["label"] for r in filas if r["criterion"] == criterio and r["split"] == particion
            ]
            if any(etiquetas.count(etiqueta) < 5 for etiqueta in ETIQUETAS):
                raise ValueError(f"{criterio}/{particion}: mínimo 5 ejemplos por clase")


def medir(real, predicho):
    p, r, f, _ = precision_recall_fscore_support(
        real, predicho, labels=ETIQUETAS, average="macro", zero_division=0
    )
    return dict(
        accuracy=float(accuracy_score(real, predicho)),
        precision_macro=float(p),
        recall_macro=float(r),
        f1_macro=float(f),
        confusion_matrix=confusion_matrix(real, predicho, labels=ETIQUETAS).tolist(),
    )


def entrenar(conjunto_datos, salida):
    filas = json.loads(conjunto_datos.read_text(encoding="utf8"))
    validar(filas)  # Rechazar datos sin revisar antes de ajustar o escribir artefactos.
    modelos, informes = {}, {}
    for criterio in CRITERIOS:
        particiones = {
            s: [r for r in filas if r["criterion"] == criterio and r["split"] == s]
            for s in ("train", "validation", "test")
        }
        candidatos = []
        for profundidad in (3, 8, None):
            for nombre, estimador in (
                (
                    "decision_tree",
                    DecisionTreeClassifier(
                        max_depth=profundidad, class_weight="balanced", random_state=42
                    ),
                ),
                (
                    "random_forest",
                    RandomForestClassifier(
                        n_estimators=150,
                        max_depth=profundidad,
                        class_weight="balanced",
                        random_state=42,
                    ),
                ),
                (
                    "logistic_regression",
                    LogisticRegression(
                        C={3: 0.1, 8: 1, None: 10}[profundidad],
                        class_weight="balanced",
                        max_iter=3000,
                    ),
                ),
            ):
                modelo = make_pipeline(DictVectorizer(), estimador)
                modelo.fit(
                    [caracteristicas(r) for r in particiones["train"]],
                    [r["label"] for r in particiones["train"]],
                )
                puntuaciones = medir(
                    [r["label"] for r in particiones["validation"]],
                    modelo.predict([caracteristicas(r) for r in particiones["validation"]]),
                )
                distancia = float(
                    np.sqrt(
                        np.mean(
                            [
                                (1 - puntuaciones[k]) ** 2
                                for k in ("accuracy", "precision_macro", "recall_macro", "f1_macro")
                            ]
                        )
                    )
                )
                candidatos.append((distancia, nombre, modelo, puntuaciones))
        _, nombre, ganador, validacion = min(candidatos, key=lambda c: c[0])
        prueba = medir(
            [r["label"] for r in particiones["test"]],
            ganador.predict([caracteristicas(r) for r in particiones["test"]]),
        )
        modelos[criterio] = ganador
        informes[criterio] = dict(
            selected=nombre,
            validation=validacion,
            test=prueba,
            approved=cumple_umbral(prueba),
            candidates=[dict(name=c[1], distance=c[0], validation=c[3]) for c in candidatos],
            samples={s: len(v) for s, v in particiones.items()},
        )
    informe = dict(
        dataset_sha256=sha256(conjunto_datos.read_bytes()).hexdigest(),
        quality_target=0.90,
        quality_approved=all(r["approved"] for r in informes.values()),
        labels=ETIQUETAS,
        criteria=informes,
        status="evaluated",
    )
    salida.mkdir(parents=True, exist_ok=True)
    # El artefacto experimental se mantiene separado del clasificador de áreas.
    joblib.dump(modelos, salida / "recomendaciones.joblib")
    informe["artifact_sha256"] = sha256(
        (salida / "recomendaciones.joblib").read_bytes()
    ).hexdigest()
    (salida / "informe.json").write_text(json.dumps(informe, indent=2), encoding="utf8")
    return informe


if __name__ == "__main__":
    argumentos_cli = argparse.ArgumentParser(description=__doc__)
    argumentos_cli.add_argument("--preparar", "--prepare", dest="preparar", action="store_true")
    argumentos_cli.add_argument(
        "--catalogo", "--catalog", dest="catalogo", type=Path, default=RAIZ / "data/catalogo.json"
    )
    argumentos_cli.add_argument(
        "--conjunto-datos",
        "--dataset",
        dest="conjunto_datos",
        type=Path,
        default=RAIZ / "data/recomendaciones/piloto.json",
    )
    argumentos_cli.add_argument(
        "--salida", "--output", dest="salida", type=Path, default=RAIZ / "models/recomendaciones"
    )
    argumentos = argumentos_cli.parse_args()
    try:
        print(
            preparar(argumentos.catalogo, argumentos.conjunto_datos)
            if argumentos.preparar
            else entrenar(argumentos.conjunto_datos, argumentos.salida)
        )
    except ValueError as error:
        argumentos_cli.exit(2, f"Entrenamiento pendiente: {error}\n")
