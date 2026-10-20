from dataclasses import replace
from decimal import Decimal

from app.adapters.output.excel import read_careers
from app.domain.criterion_analysis import analyze_criteria
from app.infrastructure.train_models import distance_to_ideal, meets_quality_target


def test_six_criteria_differences_and_actionable_recommendations(workbook):
    left = read_careers(workbook())[0]
    right = replace(
        left,
        id="C02",
        modality="Virtual",
        location="Virtual",
        monthly_cost_pen=Decimal(0),
        duration_months=48,
        requirements="Examen de admisión",
        employment="Docencia",
    )
    result = {item["key"]: item for item in analyze_criteria(left, right)}
    assert len(result) == 6
    assert all(item["relationship"] == "different" for item in result.values())
    assert "12 meses menos" in result["duration"]["explanation"]
    assert "775.00 PEN por mes menos" in result["cost"]["explanation"]
    assert right.name in result["cost"]["recommendation"]
    assert result["cost"]["right_value"] == "0.00 PEN por mes"
    assert "Docencia" in result["employment"]["explanation"]
    assert "salarios" in result["employment"]["caveats"][0]


def test_missing_and_same_are_not_winner_claims(workbook):
    left = read_careers(workbook())[0]
    right = replace(left, duration_months=None, monthly_cost_pen=None, requirements=None)
    result = {item["key"]: item for item in analyze_criteria(left, right)}
    assert result["cost"]["relationship"] == "missing"
    assert result["duration"]["right_value"] == "Dato no disponible"
    assert "falta información" in result["requirements"]["explanation"]
    assert result["modality"]["relationship"] == "same"
    assert "Todavía" not in result["modality"]["explanation"]


def test_distance_selection_and_ninety_percent_gate():
    perfect = dict(accuracy=1, precision_macro=1, recall_macro=1, f1_macro=1)
    assert distance_to_ideal(perfect) == 0
    assert meets_quality_target(perfect)
    weak = perfect | {"f1_macro": 0.89}
    assert not meets_quality_target(weak)
    assert distance_to_ideal(weak) > distance_to_ideal(perfect)
