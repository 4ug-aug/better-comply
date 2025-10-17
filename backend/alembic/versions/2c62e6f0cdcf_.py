"""empty message

Revision ID: 2c62e6f0cdcf
Revises: 37b2b331d4d3
Create Date: 2025-10-17 17:33:59.039182

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2c62e6f0cdcf'
down_revision: Union[str, Sequence[str], None] = '37b2b331d4d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('runs', 'subscription_id',
               existing_type=sa.INTEGER(),
               nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('runs', 'subscription_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    