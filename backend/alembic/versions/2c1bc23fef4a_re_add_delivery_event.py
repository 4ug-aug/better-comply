"""Re add delivery event

Revision ID: 2c1bc23fef4a
Revises: eb464cbab38e
Create Date: 2025-10-17 21:31:14.487059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2c1bc23fef4a'
down_revision: Union[str, Sequence[str], None] = 'eb464cbab38e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # remove enum from deliverystatus - We will re add it with the new table
    op.execute("DROP TYPE IF EXISTS deliverystatus")

    op.create_table('delivery_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('doc_version_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'COMPLETED', 'FAILED', name='deliverystatus'), nullable=True),
    sa.Column('artifact_type', sa.String(), nullable=False),
    sa.Column('delivery_uri', sa.String(), nullable=True),
    sa.Column('error_message', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['doc_version_id'], ['document_versions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('delivery_events')