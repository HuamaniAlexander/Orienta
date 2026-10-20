from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
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
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import relationship as relacion


class Base(DeclarativeBase):
    pass


class FilaInstitucion(Base):
    __tablename__ = "instituciones"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), unique=True)


class FilaImportacion(Base):
    __tablename__ = "importaciones"
    id: Mapped[int] = mapped_column(primary_key=True)
    sha256: Mapped[str] = mapped_column(String(64), unique=True)
    nombre_archivo: Mapped[str] = mapped_column(String(255))
    fecha_importacion: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    cantidad_filas: Mapped[int] = mapped_column(Integer)


class FilaCarrera(Base):
    __tablename__ = "ofertas_academicas"
    __table_args__ = (
        UniqueConstraint("clave_identidad", name="uq_offer_identity"),
        CheckConstraint("duracion_meses IS NULL OR duracion_meses > 0", name="ck_duration"),
        CheckConstraint("costo_mensual_soles IS NULL OR costo_mensual_soles >= 0", name="ck_cost"),
    )
    id: Mapped[str] = mapped_column(String(150), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(250))
    nombre_busqueda: Mapped[str] = mapped_column(Text)
    texto_busqueda: Mapped[str] = mapped_column(Text, default="", server_default="")
    clave_identidad: Mapped[str] = mapped_column(Text)
    id_institucion: Mapped[int] = mapped_column(ForeignKey("instituciones.id"))
    institucion: Mapped[FilaInstitucion] = relacion(lazy="joined")
    tipo_formacion: Mapped[str | None] = mapped_column(String(60))
    modalidad: Mapped[str | None] = mapped_column(String(100))
    ubicacion: Mapped[str | None] = mapped_column(String(200))
    duracion_meses: Mapped[int | None] = mapped_column(Integer)
    costo_mensual_soles: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    requisitos: Mapped[str | None] = mapped_column(Text)
    campo_laboral: Mapped[str | None] = mapped_column(Text)
    fecha_revision: Mapped[date | None] = mapped_column(Date)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    id_importacion: Mapped[int] = mapped_column(ForeignKey("importaciones.id"))
    detalles: Mapped[dict] = mapped_column(JSON, default=dict, server_default="{}")
    fuentes: Mapped[list["FilaFuente"]] = relacion(
        cascade="all, delete-orphan", lazy="selectin", order_by="FilaFuente.id"
    )


class FilaFuente(Base):
    __tablename__ = "fuentes"
    id: Mapped[int] = mapped_column(primary_key=True)
    id_oferta: Mapped[str] = mapped_column(
        String(150), ForeignKey("ofertas_academicas.id"), index=True
    )
    campo: Mapped[str] = mapped_column(String(80))
    referencia: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(Text)
