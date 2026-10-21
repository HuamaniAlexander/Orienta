"""Conservar identificadores originales y detalles del catálogo completo."""

import sqlalchemy as sa

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("fuentes", "id_oferta", type_=sa.String(150), existing_type=sa.String(30))
    op.add_column(
        "ofertas_academicas",
        sa.Column("texto_busqueda", sa.Text(), nullable=False, server_default=""),
    )
    op.execute("UPDATE ofertas_academicas SET texto_busqueda = nombre_busqueda")
    op.alter_column("ofertas_academicas", "id", type_=sa.String(150), existing_type=sa.String(30))
    op.alter_column(
        "ofertas_academicas", "nombre_busqueda", type_=sa.Text(), existing_type=sa.String(250)
    )
    op.add_column(
        "ofertas_academicas", sa.Column("detalles", sa.JSON(), nullable=False, server_default="{}")
    )


def downgrade():
    # No truncar identificadores al revertir: detener la reversión si perdería información.
    conexion = op.get_bind()
    if conexion.scalar(sa.text("SELECT COUNT(*) FROM ofertas_academicas WHERE length(id) > 30")):
        raise ValueError("Hay identificadores largos: exporta el catálogo antes de revertir")
    op.alter_column("fuentes", "id_oferta", type_=sa.String(30), existing_type=sa.String(150))
    op.drop_column("ofertas_academicas", "texto_busqueda")
    op.drop_column("ofertas_academicas", "detalles")
    op.alter_column(
        "ofertas_academicas", "nombre_busqueda", type_=sa.String(250), existing_type=sa.Text()
    )
    op.alter_column("ofertas_academicas", "id", type_=sa.String(30), existing_type=sa.String(150))
