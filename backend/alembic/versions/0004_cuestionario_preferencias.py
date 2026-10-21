"""Versiones y captura voluntaria de preferencias; sin datos personales de visitantes."""

import sqlalchemy as sa

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "definiciones_cuestionario",
        sa.Column("version", sa.String(60), primary_key=True),
        sa.Column("contenido", sa.JSON(), nullable=False),
    )
    op.create_table(
        "registros_preferencias",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("id_participante", sa.String(36), nullable=False),
        sa.Column(
            "version_cuestionario",
            sa.String(60),
            sa.ForeignKey("definiciones_cuestionario.version"),
            nullable=False,
        ),
        sa.Column("fecha_captura", sa.DateTime(timezone=True), nullable=False),
        sa.Column("estado_revision", sa.String(20), nullable=False),
        sa.Column("datos", sa.JSON(), nullable=False),
    )
    op.create_index(
        "ix_registros_preferencias_id_participante", "registros_preferencias", ["id_participante"]
    )
    # Solo FastAPI con conexión de servidor accede a elecciones de participantes.
    if op.get_bind().dialect.name == "postgresql":
        tablas = (
            "instituciones, importaciones, ofertas_academicas, fuentes, "
            "definiciones_cuestionario, registros_preferencias"
        )
        op.execute(sa.text(f"REVOKE ALL ON {tablas} FROM PUBLIC"))
        for tabla in tablas.split(", "):
            op.execute(sa.text(f"ALTER TABLE {tabla} ENABLE ROW LEVEL SECURITY"))
        for rol in ("anon", "authenticated"):
            existe = op.get_bind().scalar(
                sa.text("SELECT 1 FROM pg_roles WHERE rolname=:rol"), {"rol": rol}
            )
            if existe:
                op.execute(sa.text(f'REVOKE ALL ON {tablas} FROM "{rol}"'))


def downgrade():
    op.drop_index("ix_registros_preferencias_id_participante", table_name="registros_preferencias")
    op.drop_table("registros_preferencias")
    op.drop_table("definiciones_cuestionario")
