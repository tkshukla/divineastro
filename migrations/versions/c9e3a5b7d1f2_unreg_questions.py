"""unreg_questions table: questions typed by visitors who were not signed in

Revision ID: c9e3a5b7d1f2
Revises: b8d2f4a6c0e1
Create Date: 2026-10-06 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9e3a5b7d1f2'
down_revision: Union[str, Sequence[str], None] = 'b8d2f4a6c0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'unreg_questions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('ts', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('question', sa.String(length=500), nullable=False, server_default=''),
        sa.Column('language', sa.String(length=8), nullable=False, server_default=''),
        sa.Column('visitor', sa.String(length=16), nullable=False, server_default=''),
        sa.Column('source', sa.String(length=60), nullable=False, server_default=''),
        sa.Column('campaign', sa.String(length=80), nullable=False, server_default=''),
    )
    op.create_index('ix_unreg_questions_ts', 'unreg_questions', ['ts'])
    op.create_index('ix_unreg_questions_visitor', 'unreg_questions', ['visitor'])


def downgrade() -> None:
    op.drop_index('ix_unreg_questions_visitor', table_name='unreg_questions')
    op.drop_index('ix_unreg_questions_ts', table_name='unreg_questions')
    op.drop_table('unreg_questions')
