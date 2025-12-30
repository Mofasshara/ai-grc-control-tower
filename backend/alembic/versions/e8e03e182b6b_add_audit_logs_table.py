"""Add audit_logs table

Revision ID: e8e03e182b6b
Revises: 72681b9982b6
Create Date: 2025-12-30 18:22:37.145181

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8e03e182b6b'
down_revision: Union[str, Sequence[str], None] = '72681b9982b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=True),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("entity_type", sa.String(length=255), nullable=True),
        sa.Column("entity_id", sa.String(length=255), nullable=True),
        sa.Column("payload_hash", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("audit_logs")
