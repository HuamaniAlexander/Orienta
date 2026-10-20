import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.adapters.output.models import CareerRow, InstitutionRow
from app.domain.career import Career, Source, normalize
from app.ports.careers import CatalogQuery

FACETS = {"tipo": "training_type", "modalidad": "modality", "ubicacion": "location"}


class JsonCareerRepository:
    """Explicit read-only demo; never used as a database failure fallback."""

    def __init__(self, path: Path):
        data = json.loads(path.read_text(encoding="utf-8"))
        self.careers = [
            Career(
                **(
                    row
                    | {
                        "monthly_cost_pen": Decimal(row["monthly_cost_pen"])
                        if row["monthly_cost_pen"] is not None
                        else None,
                        "reviewed_on": date.fromisoformat(row["reviewed_on"])
                        if row["reviewed_on"]
                        else None,
                        "sources": tuple(Source(**s) for s in row["sources"]),
                    }
                )
            )
            for row in data
        ]

    def list(self, query: CatalogQuery):
        result = [
            c
            for c in self.careers
            if c.active
            and normalize(query.q) in normalize(c.name)
            and all(
                not getattr(query, key) or getattr(c, attr) == getattr(query, key)
                for key, attr in FACETS.items()
            )
        ]
        result.sort(key=lambda c: (normalize(c.name), c.institution, c.id))
        start = (query.pagina - 1) * query.limite
        return result[start : start + query.limite], len(result)

    def get(self, id: str):
        return next((c for c in self.careers if c.id == id and c.active), None)

    def facets(self):
        return {
            key: sorted({getattr(c, attr) for c in self.careers if c.active and getattr(c, attr)})
            for key, attr in FACETS.items()
        }


def to_domain(row: CareerRow) -> Career:
    return Career(
        id=row.id,
        name=row.name,
        institution=row.institution.name,
        training_type=row.training_type,
        modality=row.modality,
        location=row.location,
        duration_months=row.duration_months,
        monthly_cost_pen=row.monthly_cost_pen,
        requirements=row.requirements,
        employment=row.employment,
        reviewed_on=row.reviewed_on,
        active=row.active,
        sources=tuple(Source(s.field, s.reference, s.status) for s in row.sources),
    )


class SqlCareerRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self, query: CatalogQuery):
        conditions = [CareerRow.active.is_(True)]
        if query.q.strip():
            conditions.append(CareerRow.search_name.contains(normalize(query.q), autoescape=True))
        for key, attr in FACETS.items():
            if getattr(query, key):
                conditions.append(getattr(CareerRow, attr) == getattr(query, key))
        total = self.session.scalar(select(func.count()).select_from(CareerRow).where(*conditions))
        rows = self.session.scalars(
            select(CareerRow)
            .join(InstitutionRow)
            .where(*conditions)
            .order_by(CareerRow.search_name, InstitutionRow.name, CareerRow.id)
            .offset((query.pagina - 1) * query.limite)
            .limit(query.limite)
        ).all()
        return [to_domain(row) for row in rows], total

    def get(self, id: str):
        row = self.session.scalar(
            select(CareerRow).where(CareerRow.id == id, CareerRow.active.is_(True))
        )
        return to_domain(row) if row else None

    def facets(self):
        return {
            key: list(
                self.session.scalars(
                    select(getattr(CareerRow, attr))
                    .where(CareerRow.active.is_(True), getattr(CareerRow, attr).is_not(None))
                    .distinct()
                    .order_by(getattr(CareerRow, attr))
                )
            )
            for key, attr in FACETS.items()
        }
