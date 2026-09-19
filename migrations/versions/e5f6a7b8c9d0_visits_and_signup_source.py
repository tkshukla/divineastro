"""visits table; signup_source / signup_campaign on users

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-09-20 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'visits',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('ts', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('path', sa.String(length=200), nullable=False, server_default='/'),
        sa.Column('source', sa.String(length=60), nullable=False, server_default='direct'),
        sa.Column('medium', sa.String(length=40), nullable=False, server_default=''),
        sa.Column('campaign', sa.String(length=80), nullable=False, server_default=''),
        sa.Column('device', sa.String(length=10), nullable=False, server_default='desktop'),
        sa.Column('visitor', sa.String(length=16), nullable=False, server_default=''),
    )
    op.create_index('ix_visits_ts', 'visits', ['ts'])

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('signup_source', sa.String(length=60), nullable=True))
        batch_op.add_column(sa.Column('signup_campaign', sa.String(length=80), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('signup_campaign')
        batch_op.drop_column('signup_source')
    op.drop_index('ix_visits_ts', table_name='visits')
    op.drop_table('visits')
