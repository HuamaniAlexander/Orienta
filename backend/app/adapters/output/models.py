from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class InstitutionRow(Base):
    __tablename__ = "institutions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)


class ImportRow(Base):
    __tablename__ = "imports"
    id: Mapped[int] = mapped_column(primary_key=True)
    sha256: Mapped[str] = mapped_column(String(64), unique=True)
    filename: Mapped[str] = mapped_column(String(255))
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    row_count: Mapped[int] = mapped_column(Integer)


class CareerRow(Base):
    __tablename__ = "academic_offers"
    __table_args__ = (
        UniqueConstraint("identity_key", name="uq_offer_identity"),
        CheckConstraint("duration_months IS NULL OR duration_months > 0", name="ck_duration"),
        CheckConstraint("monthly_cost_pen IS NULL OR monthly_cost_pen >= 0", name="ck_cost"),
    )
    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(250))
    search_name: Mapped[str] = mapped_column(String(250))
    identity_key: Mapped[str] = mapped_column(Text)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"))
    institution: Mapped[InstitutionRow] = relationship(lazy="joined")
    training_type: Mapped[str | None] = mapped_column(String(60))
    modality: Mapped[str | None] = mapped_column(String(100))
    location: Mapped[str | None] = mapped_column(String(200))
    duration_months: Mapped[int | None] = mapped_column(Integer)
    monthly_cost_pen: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    requirements: Mapped[str | None] = mapped_column(Text)
    employment: Mapped[str | None] = mapped_column(Text)
    reviewed_on: Mapped[date | None] = mapped_column(Date)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    import_id: Mapped[int] = mapped_column(ForeignKey("imports.id"))
    sources: Mapped[list["SourceRow"]] = relationship(
        cascade="all, delete-orphan", lazy="selectin", order_by="SourceRow.id"
    )


class SourceRow(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    offer_id: Mapped[str] = mapped_column(ForeignKey("academic_offers.id"), index=True)
    field: Mapped[str] = mapped_column(String(80))
    reference: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
