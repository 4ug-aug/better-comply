"""Removed run id from documents

Revision ID: 679960830ae5
Revises: 2cd3b65dfa37
Create Date: 2025-10-18 14:43:33.143766

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '679960830ae5'
down_revision: Union[str, Sequence[str], None] = '2cd3b65dfa37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('documents', 'run_id')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('documents', sa.Column('run_id', sa.Integer(), nullable=True))
