import json
from pathlib import Path

import pytest

from app.adapters.output.recomendaciones_criterios import RecomendacionesRevisadas
from app.domain.recomendacion import CRITERIOS, ETIQUETAS
from app.infrastructure.entrenar_recomendaciones import (
    caracteristicas,
    cumple_umbral,
    entrenar,
    preparar,
    validar,
)


def test_piloto_separado_y_rechazo_de_etiquetas_sin_revisar(tmp_path):
    ruta = tmp_path / "pilot.json"
    preparar(Path("data/catalogo.json"), ruta)
    filas = json.loads(ruta.read_text(encoding="utf8"))
    ofertas = {
        s: {r[k] for r in filas if r["split"] == s for k in ("left_id", "right_id")}
        for s in ("train", "validation", "test")
    }
    assert not ofertas["train"] & ofertas["test"]
    assert not ofertas["train"] & ofertas["validation"]
    assert not ofertas["validation"] & ofertas["test"]
    assert all(r["label"] is None and not r["approved"] for r in filas)
    with pytest.raises(ValueError, match="revisores"):
        entrenar(ruta, tmp_path / "models")
    assert not (tmp_path / "models").exists()
    with pytest.raises(ValueError, match="ya existe"):
        preparar(Path("data/catalogo.json"), ruta)


def test_umbral_por_metrica_y_etiquetas_excluidas():
    puntuaciones = dict(accuracy=0.99, precision_macro=0.95, recall_macro=0.91, f1_macro=0.90)
    assert not cumple_umbral(puntuaciones)
    assert cumple_umbral(puntuaciones | {"f1_macro": 0.91})
    fila = dict(
        criterion="cost",
        left_value="0",
        right_value=None,
        preferences={"budget": 1000},
        label="favor_left",
        reason="secret",
    )
    assert caracteristicas(fila) == caracteristicas(
        fila | {"label": "favor_right", "reason": "different"}
    )
    assert caracteristicas(fila)["left_number"] == 0
    assert caracteristicas(fila)["right_missing"] == 1


def test_rechazo_de_par_duplicado_y_misma_oferta():
    with pytest.raises(ValueError, match="diferentes"):
        validar([dict(split="train", criterion="cost", left_id="X", right_id="X")])


def datos_revisados():
    # Etiquetas mecánicas exclusivas de pruebas; no constituyen un corpus real.
    filas = []
    for particion in ("train", "validation", "test"):
        for index in range(25):
            for criterio in CRITERIOS:
                etiqueta = ETIQUETAS[index % 5]
                filas.append(
                    dict(
                        split=particion,
                        criterion=criterio,
                        left_id=f"{particion}-{index}-left",
                        right_id=f"{particion}-{index}-right",
                        left_value=60 if criterio in ("duration", "cost") else "same",
                        right_value=60 if criterio in ("duration", "cost") else "same",
                        preferences={"budget_pen": 1000},
                        label=etiqueta,
                        reason="Test fixture only",
                        evidence=["test fixture"],
                        reviewer_1="test reviewer one",
                        reviewer_2="test reviewer two",
                        reviewer_1_label=etiqueta,
                        reviewer_2_label=etiqueta,
                        approved=True,
                    )
                )
    return filas


def test_entrenamiento_completo_y_control_de_calidad_independiente(tmp_path):
    ruta = tmp_path / "test-only.json"
    ruta.write_text(json.dumps(datos_revisados()), encoding="utf8")
    informe = entrenar(ruta, tmp_path / "models")
    assert not informe["quality_approved"]
    assert set(informe["criteria"]) == set(CRITERIOS)
    for criterio in informe["criteria"].values():
        assert len(criterio["candidates"]) == 9
        assert sum(map(sum, criterio["test"]["confusion_matrix"])) == 25
    estado, predicciones = RecomendacionesRevisadas(tmp_path / "models").analizar(None, None, {})
    assert estado["status"] == "below_quality_target"
    assert not predicciones


def test_rechazo_de_fugas_y_desacuerdos_sin_resolver():
    filas = datos_revisados()
    filas[-1]["left_id"] = filas[0]["left_id"]
    with pytest.raises(ValueError, match="Fuga"):
        validar(filas)
    filas = datos_revisados()
    filas[0]["reviewer_2_label"] = "insufficient_data"
    with pytest.raises(ValueError, match="desacuerdo"):
        validar(filas)
