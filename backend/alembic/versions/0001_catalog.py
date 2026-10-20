"""Institutions, imports, academic offers and field sources."""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "institutions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False, unique=True),
    )
    op.create_table(
        "imports",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("sha256", sa.String(64), nullable=False, unique=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("row_count", sa.Integer, nullable=False),
    )
    op.create_table(
        "academic_offers",
        sa.Column("id", sa.String(30), primary_key=True),
        sa.Column("name", sa.String(250), nullable=False),
        sa.Column("search_name", sa.String(250), nullable=False),
        sa.Column("identity_key", sa.Text, nullable=False),
        sa.Column("institution_id", sa.Integer, sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("training_type", sa.String(60)),
        sa.Column("modality", sa.String(100)),
        sa.Column("location", sa.String(200)),
        sa.Column("duration_months", sa.Integer),
        sa.Column("monthly_cost_pen", sa.Numeric(12, 2)),
        sa.Column("requirements", sa.Text),
        sa.Column("employment", sa.Text),
        sa.Column("reviewed_on", sa.Date),
        sa.Column("active", sa.Boolean, nullable=False),
        sa.Column("import_id", sa.Integer, sa.ForeignKey("imports.id"), nullable=False),
        sa.UniqueConstraint("identity_key", name="uq_offer_identity"),
        sa.CheckConstraint("duration_months IS NULL OR duration_months > 0", name="ck_duration"),
        sa.CheckConstraint("monthly_cost_pen IS NULL OR monthly_cost_pen >= 0", name="ck_cost"),
    )
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("offer_id", sa.String(30), sa.ForeignKey("academic_offers.id"), nullable=False),
        sa.Column("field", sa.String(80), nullable=False),
        sa.Column("reference", sa.Text),
        sa.Column("status", sa.Text, nullable=False),
    )
    op.create_index("ix_sources_offer_id", "sources", ["offer_id"])


def downgrade():
    op.drop_table("sources")
    op.drop_table("academic_offers")
    op.drop_table("imports")
    op.drop_table("institutions")
