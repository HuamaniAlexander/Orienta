from dataclasses import replace
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.adapters.output.excel import read_careers
from app.domain.comparison import InvalidComparison, compare
from app.infrastructure.main import create_app
from app.infrastructure.settings import Settings


def test_two_distinct_and_missing_values(workbook):
    left = read_careers(workbook())[0]
    with pytest.raises(InvalidComparison):
        compare(left, left)
    right = replace(
        left, id="C02", modality="Virtual", duration_months=None, monthly_cost_pen=Decimal(0)
    )
    result = compare(left, right)
    assert result.duration_difference_months is None
    assert result.monthly_cost_difference_pen == Decimal(-775)
    assert compare(right, left).monthly_cost_difference_pen == Decimal(775)


def test_comparison_contract():
    with TestClient(create_app(Settings(data_mode="demo"))) as client:
        for ids in [[], ["C01"], ["C01", "C01"], ["C01", "C02", "C03"]]:
            assert client.post("/api/comparaciones", json={"career_ids": ids}).status_code == 422
        result = client.post("/api/comparaciones", json={"career_ids": ["C01", "C05"]})
        assert result.status_code == 200
        assert result.json()["monthly_cost_difference_pen"] == "-775"
        assert result.json()["duration_difference_months"] == 0
        assert (
            client.post("/api/comparaciones", json={"career_ids": ["C01", "no"]}).status_code == 404
        )
