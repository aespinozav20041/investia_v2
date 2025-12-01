"""add billing fields to user"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_add_billing_fields"
down_revision = "0001_create_model_versions"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("upgraded_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("enterprise_requested", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("last_payment_id", sa.String(), nullable=True))
    op.add_column("users", sa.Column("last_payment_status", sa.String(), nullable=True))


def downgrade():
    op.drop_column("users", "last_payment_status")
    op.drop_column("users", "last_payment_id")
    op.drop_column("users", "enterprise_requested")
    op.drop_column("users", "upgraded_at")
