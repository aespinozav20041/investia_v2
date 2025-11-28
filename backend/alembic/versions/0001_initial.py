"""initial tables"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.domain.ml.models import ModelStatus

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("code", sa.Text(), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("max_signals_per_day", sa.Integer(), nullable=False),
        sa.Column("max_capital_per_user", sa.Numeric(), nullable=False),
        sa.Column("data_delay_seconds", sa.Integer(), nullable=False),
        sa.Column("is_enterprise", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("allowed_symbols", postgresql.ARRAY(sa.String()), nullable=True),
    )
    op.create_index("ix_plans_code", "plans", ["code"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plans.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "model_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("tier", sa.Text(), nullable=False),
        sa.Column("enterprise_slug", sa.Text(), nullable=True),
        sa.Column("symbol_universe", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("status", sa.Enum(ModelStatus, name="modelstatus"), nullable=False),
        sa.Column("mlflow_run_id", sa.Text(), nullable=True),
        sa.Column("mlflow_model_uri", sa.Text(), nullable=False),
        sa.Column("sharpe", sa.Numeric(), nullable=True),
        sa.Column("max_drawdown", sa.Numeric(), nullable=True),
        sa.Column("trained_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("symbol", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("signal_value", sa.Numeric(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("model_name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "trades",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("symbol", sa.Text(), nullable=False),
        sa.Column("side", sa.Text(), nullable=False),
        sa.Column("qty", sa.Numeric(), nullable=False),
        sa.Column("entry_price", sa.Numeric(), nullable=False),
        sa.Column("exit_price", sa.Numeric(), nullable=True),
        sa.Column("pnl", sa.Numeric(), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("trades")
    op.drop_table("signals")
    op.drop_table("model_versions")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_plans_code", table_name="plans")
    op.drop_table("plans")
    op.execute("DROP TYPE IF EXISTS modelstatus")
