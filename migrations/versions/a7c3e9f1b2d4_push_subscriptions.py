"""push_subscriptions table (DIVASTRO-112 daily web push)

Revision ID: a7c3e9f1b2d4
Revises: f2a3b4c5d6e7
Create Date: 2026-10-03 12:00:00.000000

Plain strings and integers only — no database enum (see HANDOVER: SQLite
cannot catch Postgres enum drift).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7c3e9f1b2d4'
down_revision: Union[str, Sequence[str], None] = 'f2a3b4c5d6e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'push_subscriptions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('endpoint', sa.String(length=1000), nullable=False),
        sa.Column('p256dh', sa.String(length=200), nullable=False),
        sa.Column('auth', sa.String(length=64), nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lon', sa.Float(), nullable=False),
        sa.Column('tz', sa.String(length=64), nullable=False, server_default='Asia/Kolkata'),
        sa.Column('city', sa.String(length=120), nullable=False, server_default=''),
        sa.Column('lang', sa.String(length=5), nullable=False, server_default='en'),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('last_sent', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failures', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL',
                                name='fk_push_subscriptions_user_id_users'),
        sa.UniqueConstraint('endpoint', name='uq_push_subscriptions_endpoint'),
    )
    op.create_index('ix_push_subscriptions_user_id', 'push_subscriptions', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_push_subscriptions_user_id', table_name='push_subscriptions')
    op.drop_table('push_subscriptions')
