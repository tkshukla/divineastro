"""Guest checkout (DIVASTRO-158): orders.guest_email/guest_phone/guest_json + emailed_answer_jobs.order_id

Revision ID: f3b5d7e9a1c4
Revises: e7a1c3d5f9b2
Create Date: 2026-10-21 00:00:00.000000

All columns are nullable with no default: every existing order is a signed-in order
(NULL = not a guest order) and every existing job was asked in the app (order_id NULL),
so the upgrade needs no data step. Only this file's `down_revision` has to change if
another migration lands first (re-chain it onto the new head).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3b5d7e9a1c4'
down_revision: Union[str, Sequence[str], None] = 'e7a1c3d5f9b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('guest_email', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('guest_phone', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('guest_json', sa.Text(), nullable=True))

    with op.batch_alter_table('emailed_answer_jobs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('order_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_emailed_answer_jobs_order_id_orders', 'orders', ['order_id'], ['id'],
            ondelete='SET NULL')
        batch_op.create_index('ix_emailed_answer_jobs_order_id', ['order_id'])


def downgrade() -> None:
    with op.batch_alter_table('emailed_answer_jobs', schema=None) as batch_op:
        batch_op.drop_index('ix_emailed_answer_jobs_order_id')
        batch_op.drop_constraint('fk_emailed_answer_jobs_order_id_orders', type_='foreignkey')
        batch_op.drop_column('order_id')

    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_column('guest_json')
        batch_op.drop_column('guest_phone')
        batch_op.drop_column('guest_email')
