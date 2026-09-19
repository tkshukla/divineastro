"""feedback table; blocked_reason / blocked_at / blocked_by on users

Revision ID: d4e5f6a7b8c9
Revises: c9d8e7f6a5b4
Create Date: 2026-09-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'c9d8e7f6a5b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'feedback',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('category', sa.String(length=20), nullable=False, server_default='general'),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('page', sa.String(length=120), nullable=False, server_default=''),
        sa.Column('allow_contact', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('status', sa.String(length=12), nullable=False, server_default='new'),
        sa.Column('admin_note', sa.Text(), nullable=False, server_default=''),
        sa.Column('handled_by', sa.Integer(), nullable=True),
        sa.Column('handled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index('ix_feedback_user_id', 'feedback', ['user_id'])
    op.create_index('ix_feedback_status', 'feedback', ['status'])
    op.create_index('ix_feedback_created_at', 'feedback', ['created_at'])

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('blocked_reason', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('blocked_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('blocked_by', sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('blocked_by')
        batch_op.drop_column('blocked_at')
        batch_op.drop_column('blocked_reason')
    op.drop_index('ix_feedback_created_at', table_name='feedback')
    op.drop_index('ix_feedback_status', table_name='feedback')
    op.drop_index('ix_feedback_user_id', table_name='feedback')
    op.drop_table('feedback')
