"""Symmetric inputs without names, areas, groups or identifiers as predictors."""

import json
from hashlib import sha256

from app.domain.career import Career

NUMERIC = ["cost_difference", "cost_mean", "duration_difference", "duration_mean"]
CATEGORICAL = ["institution_a", "institution_b", "modality_a", "modality_b"]


def signature(c: Career) -> str:
    values = [
        c.id,
        c.name,
        c.institution,
        c.modality,
        c.location,
        c.duration_months,
        format(c.monthly_cost_pen, ".2f") if c.monthly_cost_pen is not None else None,
        c.employment,
        c.requirements,
    ]
    return sha256(json.dumps(values, ensure_ascii=False).encode()).hexdigest()


def features(left: Career, right: Career) -> dict:
    a, b = sorted([left, right], key=lambda c: c.id)
    row = {}
    for prefix, values in [
        ("cost", [a.monthly_cost_pen, b.monthly_cost_pen]),
        ("duration", [a.duration_months, b.duration_months]),
    ]:
        if any(v is None for v in values):
            row[prefix + "_difference"] = float("nan")
            row[prefix + "_mean"] = float("nan")
        else:
            row[prefix + "_difference"] = abs(float(values[0]) - float(values[1]))
            row[prefix + "_mean"] = (float(values[0]) + float(values[1])) / 2
    for suffix, c in [("a", a), ("b", b)]:
        row["institution_" + suffix] = c.institution
        row["modality_" + suffix] = c.modality or "Sin modalidad"
    return row
