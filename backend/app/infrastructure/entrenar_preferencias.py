"""Entrenamiento offline. Solo acepta elecciones reales autorizadas y revisadas."""

import argparse
import json
import platform
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.adapters.output.repositorios_carreras import RepositorioCarrerasJson
from app.application.recomendar_preferencia import huella_programas
from app.domain.cuestionario import VERSION_CUESTIONARIO, generar_cuestionario, validar_respuestas
from app.domain.perfil_vocacional import VERSION_CARACTERISTICAS, extraer_caracteristicas


def validar_dataset(filas, carreras):
    registros, ids = [], set()
    for fila in filas:
        if fila["id_registro"] in ids:
            raise ValueError("Registros duplicados")
        ids.add(fila["id_registro"])
        if (
            not fila.get("consentimiento")
            or not fila.get("mayor_edad")
            or fila.get("estado_revision") != "aprobado"
        ):
            raise ValueError("Faltan consentimiento, mayoría de edad o revisión de calidad")
        if fila.get("origen_eleccion") != "previa_inferencia":
            raise ValueError("La etiqueta requiere una elección independiente previa")
        if (
            fila.get("version_cuestionario") != VERSION_CUESTIONARIO
            or fila.get("version_caracteristicas") != VERSION_CARACTERISTICAS
        ):
            raise ValueError("Versiones incompatibles")
        a, b = [carreras[identificador] for identificador in sorted(fila["programas"])]
        if a.id == b.id or not a.activa or not b.activa:
            raise ValueError("Par no válido")
        if huella_programas([a, b]) != fila["huella_programas"]:
            raise ValueError("Las fichas cambiaron desde la captura; revisar antes de entrenar")
        validar_respuestas(generar_cuestionario(a, b), fila["respuestas"], fila["preferencias"])
        caracteristicas = extraer_caracteristicas(a, b, fila["respuestas"], fila["preferencias"])
        if caracteristicas != fila["caracteristicas"]:
            raise ValueError("Características divergentes respecto al esquema actual")
        if not fila.get("id_participante"):
            raise ValueError("Falta identificador seudónimo del participante")
        if fila["eleccion"] not in (a.id, b.id, "ambas", "ninguna", "incierto"):
            raise ValueError("Etiqueta ajena al par")
        if fila["eleccion"] in (a.id, b.id):
            registros.append(
                (caracteristicas, int(fila["eleccion"] == a.id), fila["id_participante"])
            )
    if len({r[2] for r in registros}) < 30:
        raise ValueError(
            (
                "Se requieren al menos 30 participantes con elecciones revisadas; "
                "es un mínimo operativo, no garantía de validez"
            )
        )
    return registros


def separar_participantes(registros):
    grupos = np.array([r[2] for r in registros])
    indices = np.arange(len(registros))
    entrenamiento_validacion, prueba = next(
        GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42).split(indices, groups=grupos)
    )
    entrenamiento_local, validacion_local = next(
        GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=43).split(
            entrenamiento_validacion, groups=grupos[entrenamiento_validacion]
        )
    )
    particiones = [
        entrenamiento_validacion[entrenamiento_local],
        entrenamiento_validacion[validacion_local],
        prueba,
    ]
    for particion in particiones:
        if len({registros[i][1] for i in particion}) != 2:
            raise ValueError(
                "Cada partición necesita ambas preferencias; recopila más participantes"
            )
    return particiones


def evaluar(modelo, x, y):
    prediccion = modelo.predict(x)
    return {
        "accuracy": accuracy_score(y, prediccion),
        "balanced_accuracy": balanced_accuracy_score(y, prediccion),
        "precision": precision_score(y, prediccion, average="macro", zero_division=0),
        "recall": recall_score(y, prediccion, average="macro", zero_division=0),
        "f1": f1_score(y, prediccion, average="macro", zero_division=0),
        "matriz_confusion": confusion_matrix(y, prediccion, labels=[0, 1]).tolist(),
        "brier": brier_score_loss(y, modelo.predict_proba(x)[:, 1]),
    }


def entrenar(filas, carreras, salida):
    registros = validar_dataset(filas, carreras)
    entrenamiento, validacion, prueba = separar_participantes(registros)
    x_entrenamiento = [registros[i][0] for i in entrenamiento]
    y_entrenamiento = [registros[i][1] for i in entrenamiento]
    # Aumentar solo entrenamiento: preservar participantes y evitar sesgo de posición.
    x_ampliado = x_entrenamiento + [{k: -v for k, v in x.items()} for x in x_entrenamiento]
    y_ampliado = y_entrenamiento + [1 - y for y in y_entrenamiento]
    x_validacion, y_validacion = (
        [registros[i][0] for i in validacion],
        [registros[i][1] for i in validacion],
    )
    candidatos = []
    for c in (0.1, 1.0, 10.0):
        modelo = Pipeline(
            [
                ("vectorizador", DictVectorizer(sparse=False)),
                ("escalador", StandardScaler(with_mean=False)),
                (
                    "clasificador",
                    LogisticRegression(C=c, fit_intercept=False, random_state=42, max_iter=2000),
                ),
            ]
        )
        modelo.fit(x_ampliado, y_ampliado)
        candidatos.append((evaluar(modelo, x_validacion, y_validacion)["f1"], -c, modelo, c))
    _, _, modelo, c = max(candidatos, key=lambda item: item[:2])
    x_prueba, y_prueba = [registros[i][0] for i in prueba], [registros[i][1] for i in prueba]
    referencia = DummyClassifier(strategy="most_frequent").fit(
        np.zeros((len(entrenamiento), 1)), y_entrenamiento
    )
    metricas = evaluar(modelo, x_prueba, y_prueba)
    base = evaluar(referencia, np.zeros((len(prueba), 1)), y_prueba)
    habilitado = (
        all(metricas[k] > 0.90 for k in ("accuracy", "precision", "recall", "f1"))
        and metricas["accuracy"] > base["accuracy"]
        and metricas["f1"] > base["f1"]
    )
    if (salida / "informe.json").exists() or (salida / "preferencias.joblib").exists():
        raise ValueError("Usa un directorio nuevo para conservar la versión entrenada anterior")
    salida.mkdir(parents=True, exist_ok=True)
    ruta = salida / "preferencias.joblib"
    joblib.dump(modelo, ruta)
    informe = {
        "version": "preferencias-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "version_caracteristicas": VERSION_CARACTERISTICAS,
        "version_cuestionario": VERSION_CUESTIONARIO,
        "sha256": sha256(ruta.read_bytes()).hexdigest(),
        "habilitado": habilitado,
        "umbral_calidad": 0.90,
        "C": c,
        "validacion": evaluar(modelo, x_validacion, y_validacion),
        "prueba": metricas,
        "referencia": base,
        "particiones": {
            nombre: {
                "registros": len(indices),
                "participantes": len({registros[i][2] for i in indices}),
            }
            for nombre, indices in zip(
                ("entrenamiento", "validacion", "prueba"),
                (entrenamiento, validacion, prueba),
                strict=True,
            )
        },
        "version_python": platform.python_version(),
        "version_sklearn": sklearn.__version__,
        "semillas": [42, 43],
        "limitaciones": [
            (
                "Muestra voluntaria; evaluar sesgos de selección y cobertura antes"
                " de una entrega pública."
            ),
            (
                "Las categorías RIASEC son correspondencias orientativas del "
                "contenido, no un instrumento validado."
            ),
            (
                "La evaluación no garantiza éxito profesional. Las probabilidades "
                "no se muestran como confianza al usuario."
            ),
        ],
    }
    (salida / "informe.json").write_text(
        json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return informe


def principal():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, required=True)
    parser.add_argument("--catalogo", type=Path, default=Path("data/catalogo_lima_norte_2026.json"))
    parser.add_argument("--salida", type=Path, default=Path("models/preferencias"))
    argumentos = parser.parse_args()
    filas = [
        json.loads(linea)
        for linea in argumentos.datos.read_text(encoding="utf-8").splitlines()
        if linea.strip()
    ]
    carreras = {c.id: c for c in RepositorioCarrerasJson(argumentos.catalogo).carreras}
    print(json.dumps(entrenar(filas, carreras, argumentos.salida), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    principal()
