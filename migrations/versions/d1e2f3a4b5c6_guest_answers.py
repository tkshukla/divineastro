"""guest_answers table: the one free answer a signed-out visitor may get (DIVASTRO-154)

Revision ID: d1e2f3a4b5c6
Revises: c9e3a5b7d1f2
Create Date: 2026-10-09 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, Sequence[str], None] = 'c9e3a5b7d1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No IP, no user id, no birth details: see app/db.py GuestAnswer.
    op.create_table(
        'guest_answers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('ts', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('visitor', sa.String(length=16), nullable=False, server_default=''),
        sa.Column('question', sa.String(length=500), nullable=False, server_default=''),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=8), nullable=False, server_default=''),
    )
    op.create_index('ix_guest_answers_ts', 'guest_answers', ['ts'])
    op.create_index('ix_guest_answers_visitor', 'guest_answers', ['visitor'])


def downgrade() -> None:
    op.drop_index('ix_guest_answers_visitor', table_name='guest_answers')
    op.drop_index('ix_guest_answers_ts', table_name='guest_answers')
    op.drop_table('guest_answers')
