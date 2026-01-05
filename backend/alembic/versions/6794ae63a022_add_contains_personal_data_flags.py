"""add_contains_personal_data_flags

Revision ID: 6794ae63a022
Revises: e4548b0ff8da
Create Date: 2026-01-05 15:06:33.895444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6794ae63a022'
down_revision: Union[str, Sequence[str], None] = 'e4548b0ff8da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add contains_personal_data columns to ai_incidents and change_requests tables."""
    # Add contains_personal_data to ai_incidents
    op.add_column(
        'ai_incidents',
        sa.Column('contains_personal_data', sa.Boolean(), nullable=False, server_default='false')
    )

    # Add contains_personal_data to change_requests
    op.add_column(
        'change_requests',
        sa.Column('contains_personal_data', sa.Boolean(), nullable=False, server_default='false')
    )


def downgrade() -> None:
    """Remove contains_personal_data columns from ai_incidents and change_requests tables."""
    # Remove contains_personal_data from change_requests
    op.drop_column('change_requests', 'contains_personal_data')

    # Remove contains_personal_data from ai_incidents
    op.drop_column('ai_incidents', 'contains_personal_data')
