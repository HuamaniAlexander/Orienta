import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.output.excel import read_careers
from app.adapters.output.models import CareerRow, ImportRow, InstitutionRow, SourceRow
from app.domain.career import Career, normalize


def import_workbook(path: Path, session: Session) -> dict[str, int | bool]:
    # Validate every row before opening the write transaction.
    content_hash = sha256(path.read_bytes()).hexdigest()
    careers = read_careers(path)
    return import_careers(careers, content_hash, path.name, session)


def import_careers(
    careers: list[Career], content_hash: str, filename: str, session: Session
) -> dict[str, int | bool]:
    if (
        not careers
        or len({c.id for c in careers}) != len(careers)
        or len({c.identity for c in careers}) != len(careers)
    ):
        raise ValueError("El catálogo está vacío o contiene duplicados")
    with session.begin():
        # Serializes concurrent imports on PostgreSQL; unique constraints remain the final guard.
        if session.bind.dialect.name == "postgresql":
            from sqlalchemy import text

            session.execute(text("SELECT pg_advisory_xact_lock(710013)"))
        previous = session.scalar(select(ImportRow).where(ImportRow.sha256 == content_hash))
        if previous:
            return {"rows": previous.row_count, "unchanged": True}
        batch = ImportRow(
            sha256=content_hash,
            filename=filename,
            row_count=len(careers),
            imported_at=datetime.now(timezone.utc),
        )
        session.add(batch)
        session.flush()
        for career in careers:
            institution = session.scalar(
                select(InstitutionRow).where(InstitutionRow.name == career.institution)
            )
            if institution is None:
                institution = InstitutionRow(name=career.institution)
                session.add(institution)
                session.flush()
            row = session.get(CareerRow, career.id)
            identity_key = json.dumps(career.identity, ensure_ascii=False)
            conflict = session.scalar(
                select(CareerRow).where(
                    CareerRow.identity_key == identity_key, CareerRow.id != career.id
                )
            )
            if conflict:
                raise ValueError(f"Identidad ya asociada al código {conflict.id}")
            if row is None:
                row = CareerRow(id=career.id)
                session.add(row)
            for key in (
                "name",
                "training_type",
                "modality",
                "location",
                "duration_months",
                "monthly_cost_pen",
                "requirements",
                "employment",
                "reviewed_on",
                "active",
            ):
                setattr(row, key, getattr(career, key))
            row.institution_id = institution.id
            row.search_name = normalize(career.name)
            row.identity_key = identity_key
            row.import_id = batch.id
            row.sources = [
                SourceRow(
                    field=s.field, reference=s.reference, status=s.status or "Sin estado registrado"
                )
                for s in career.sources
            ]
            session.flush()
    return {"rows": len(careers), "unchanged": False}
