from dataclasses import replace
from decimal import Decimal

from app.adapters.output.excel import leer_carreras
from app.domain.analisis_criterios import analizar_criterios
from app.infrastructure.entrenar_modelos import cumple_objetivo_calidad, distancia_al_ideal


def test_seis_criterios_diferencias_y_recomendaciones(libro_datos):
    izquierda = leer_carreras(libro_datos())[0]
    derecha = replace(
        izquierda,
        id="C02",
        modalidad="Virtual",
        ubicacion="Virtual",
        costo_mensual_soles=Decimal(0),
        duracion_meses=48,
        requisitos="Examen de admisión",
        campo_laboral="Docencia",
    )
    resultado = {elemento["clave"]: elemento for elemento in analizar_criterios(izquierda, derecha)}
    assert len(resultado) == 6
    assert all(elemento["relacion"] == "different" for elemento in resultado.values())
    assert "12 meses menos" in resultado["duration"]["explicacion"]
    assert "775.00 PEN por mes menos" in resultado["cost"]["explicacion"]
    assert derecha.nombre in resultado["cost"]["recomendacion"]
    assert resultado["cost"]["valor_derecha"] == "0.00 PEN por mes"
    assert "Docencia" in resultado["employment"]["explicacion"]
    assert "salarios" in resultado["employment"]["advertencias"][0]


def test_faltantes_e_iguales_no_eligen_ganadora(libro_datos):
    izquierda = leer_carreras(libro_datos())[0]
    derecha = replace(izquierda, duracion_meses=None, costo_mensual_soles=None, requisitos=None)
    resultado = {elemento["clave"]: elemento for elemento in analizar_criterios(izquierda, derecha)}
    assert resultado["cost"]["relacion"] == "missing"
    assert resultado["duration"]["valor_derecha"] == "Dato no disponible"
    assert "falta información" in resultado["requirements"]["explicacion"]
    assert resultado["modality"]["relacion"] == "same"
    assert "Todavía" not in resultado["modality"]["explicacion"]


def test_seleccion_por_distancia_y_umbral_calidad():
    perfecto = dict(accuracy=1, precision_macro=1, recall_macro=1, f1_macro=1)
    assert distancia_al_ideal(perfecto) == 0
    assert cumple_objetivo_calidad(perfecto)
    debil = perfecto | {"f1_macro": 0.89}
    assert not cumple_objetivo_calidad(debil)
    assert distancia_al_ideal(debil) > distancia_al_ideal(perfecto)
