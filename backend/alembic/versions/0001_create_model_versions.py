"""create model_versions table"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_create_model_versions"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "model_versions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("plan", sa.String, nullable=False),
        sa.Column("uri", sa.String, nullable=False),
        sa.Column("sharpe", sa.Float, nullable=False),
        sa.Column("win_rate", sa.Float, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_model_versions_plan", "model_versions", ["plan"])


def downgrade():
    op.drop_index("ix_model_versions_plan", table_name="model_versions")
    op.drop_table("model_versions")
