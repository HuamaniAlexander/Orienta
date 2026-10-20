from dataclasses import dataclass
from decimal import Decimal

from app.domain.career import Career


class InvalidComparison(Exception):
    pass


@dataclass(frozen=True)
class Comparison:
    left: Career
    right: Career
    duration_difference_months: int | None
    monthly_cost_difference_pen: Decimal | None


def compare(left: Career, right: Career) -> Comparison:
    if left.id == right.id or left.identity == right.identity:
        raise InvalidComparison("Selecciona dos alternativas diferentes")
    duration = (
        None
        if left.duration_months is None or right.duration_months is None
        else (right.duration_months - left.duration_months)
    )
    cost = (
        None
        if left.monthly_cost_pen is None or right.monthly_cost_pen is None
        else (right.monthly_cost_pen - left.monthly_cost_pen)
    )
    return Comparison(left, right, duration, cost)
