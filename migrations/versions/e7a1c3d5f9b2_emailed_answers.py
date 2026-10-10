"""Starter emailed answers (DIVASTRO-155): credit_entries.credit_type + emailed_answer_jobs

Revision ID: e7a1c3d5f9b2
Revises: d1e2f3a4b5c6
Create Date: 2026-10-11 00:00:00.000000

credit_entries.credit_type separates the Starter's emailed-answer balance from the
instant-answer balance. Every existing row is an instant-answer row, so the column
is NOT NULL with server_default 'question': the upgrade needs no data step and every
balance stays exactly what it was. A plain string, not a DB enum (see app/db.py).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7a1c3d5f9b2'
down_revision: Union[str, Sequence[str], None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('credit_entries', schema=None) as batch_op:
        batch_op.add_column(sa.Column('credit_type', sa.String(length=12), nullable=False,
                                      server_default='question'))

    op.create_table(
        'emailed_answer_jobs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey(
            'users.id', name='fk_emailed_answer_jobs_user_id_users'), nullable=False),
        sa.Column('birth_id', sa.Integer(), sa.ForeignKey(
            'birth_profiles.id', name='fk_emailed_answer_jobs_birth_id_birth_profiles',
            ondelete='SET NULL'), nullable=True),
        sa.Column('birth_json', sa.Text(), nullable=False, server_default=''),
        sa.Column('chart_name', sa.String(length=120), nullable=False, server_default=''),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=5), nullable=False, server_default='en'),
        sa.Column('as_of', sa.String(length=32), nullable=False, server_default=''),
        sa.Column('email', sa.String(length=255), nullable=False, server_default=''),
        sa.Column('status', sa.String(length=10), nullable=False, server_default='pending'),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('model_used', sa.String(length=80), nullable=False, server_default=''),
        sa.Column('translator', sa.String(length=80), nullable=False, server_default=''),
        sa.Column('route_reason', sa.String(length=40), nullable=False, server_default=''),
        sa.Column('answer', sa.Text(), nullable=False, server_default=''),
        sa.Column('error', sa.Text(), nullable=False, server_default=''),
        sa.Column('emailed', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('refunded', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('question_id', sa.Integer(), sa.ForeignKey(
            'questions.id', name='fk_emailed_answer_jobs_question_id_questions',
            ondelete='SET NULL'), nullable=True),
        sa.Column('visitor', sa.String(length=16), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_emailed_answer_jobs_user_id', 'emailed_answer_jobs', ['user_id'])
    op.create_index('ix_emailed_answer_jobs_status', 'emailed_answer_jobs', ['status'])
    op.create_index('ix_emailed_answer_jobs_created_at', 'emailed_answer_jobs', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_emailed_answer_jobs_created_at', table_name='emailed_answer_jobs')
    op.drop_index('ix_emailed_answer_jobs_status', table_name='emailed_answer_jobs')
    op.drop_index('ix_emailed_answer_jobs_user_id', table_name='emailed_answer_jobs')
    op.drop_table('emailed_answer_jobs')
    # Emailed-answer ledger rows would otherwise silently join the instant balance
    # once the column is gone: drop them first (a downgrade is a deliberate undo).
    op.execute("DELETE FROM credit_entries WHERE credit_type <> 'question'")
    with op.batch_alter_table('credit_entries', schema=None) as batch_op:
        batch_op.drop_column('credit_type')
