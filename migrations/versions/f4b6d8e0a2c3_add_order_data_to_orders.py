"""add order_data to orders (DIVASTRO-156)

Per-order data a product needs that is not a saved chart, as JSON text. The
Kundali Milan report keeps both people's birth details here, plus the address
its PDF is emailed to.

Revision ID: f4b6d8e0a2c3
Revises: e7a1c3d5f9b2
Create Date: 2026-10-21 22:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4b6d8e0a2c3'
down_revision: Union[str, Sequence[str], None] = 'e7a1c3d5f9b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('order_data', sa.Text(), nullable=False, server_default=''))


def downgrade() -> None:
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_column('order_data')
