"""Renombrar tablas y columnas propias sin copiar ni eliminar registros."""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

CAMBIOS = {
    "institutions": ("instituciones", {"name": "nombre"}),
    "imports": (
        "importaciones",
        {
            "filename": "nombre_archivo",
            "imported_at": "fecha_importacion",
            "row_count": "cantidad_filas",
        },
    ),
    "academic_offers": (
        "ofertas_academicas",
        {
            "name": "nombre",
            "search_name": "nombre_busqueda",
            "identity_key": "clave_identidad",
            "institution_id": "id_institucion",
            "training_type": "tipo_formacion",
            "modality": "modalidad",
            "location": "ubicacion",
            "duration_months": "duracion_meses",
            "monthly_cost_pen": "costo_mensual_soles",
            "requirements": "requisitos",
            "employment": "campo_laboral",
            "reviewed_on": "fecha_revision",
            "active": "activa",
            "import_id": "id_importacion",
        },
    ),
    "sources": (
        "fuentes",
        {"offer_id": "id_oferta", "field": "campo", "reference": "referencia", "status": "estado"},
    ),
}


def upgrade():
    for anterior, (actual, columnas) in CAMBIOS.items():
        for columna_anterior, columna_actual in columnas.items():
            op.alter_column(anterior, columna_anterior, new_column_name=columna_actual)
        op.rename_table(anterior, actual)
    op.drop_index("ix_sources_offer_id", table_name="fuentes")
    op.create_index("ix_fuentes_id_oferta", "fuentes", ["id_oferta"])


def downgrade():
    op.drop_index("ix_fuentes_id_oferta", table_name="fuentes")
    op.create_index("ix_sources_offer_id", "fuentes", ["id_oferta"])
    for anterior, (actual, columnas) in reversed(list(CAMBIOS.items())):
        op.rename_table(actual, anterior)
        for columna_anterior, columna_actual in reversed(list(columnas.items())):
            op.alter_column(anterior, columna_actual, new_column_name=columna_anterior)
