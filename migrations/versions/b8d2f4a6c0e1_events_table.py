"""events table: in-app actions for the admin Traffic panel

Revision ID: b8d2f4a6c0e1
Revises: a7c3e9f1b2d4
Create Date: 2026-10-04 23:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8d2f4a6c0e1'
down_revision: Union[str, Sequence[str], None] = 'a7c3e9f1b2d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('ts', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('name', sa.String(length=30), nullable=False, server_default=''),
        sa.Column('detail', sa.String(length=60), nullable=False, server_default=''),
        sa.Column('visitor', sa.String(length=16), nullable=False, server_default=''),
        sa.Column('source', sa.String(length=60), nullable=False, server_default=''),
        sa.Column('campaign', sa.String(length=80), nullable=False, server_default=''),
    )
    op.create_index('ix_events_ts', 'events', ['ts'])
    op.create_index('ix_events_visitor', 'events', ['visitor'])


def downgrade() -> None:
    op.drop_index('ix_events_visitor', table_name='events')
    op.drop_index('ix_events_ts', table_name='events')
    op.drop_table('events')
