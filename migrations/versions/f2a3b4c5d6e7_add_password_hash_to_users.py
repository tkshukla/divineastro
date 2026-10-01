"""add password_hash to users

Revision ID: f2a3b4c5d6e7
Revises: e5f6a7b8c9d0
Create Date: 2026-10-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2a3b4c5d6e7'
down_revision: Union[str, Sequence[str], None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add password_hash for the new username/password sign-in path.

    Nullable, no server_default: every existing row is an OAuth or dev-login
    account and genuinely has no password — NULL means "not a password
    account", not "unset". Identity and uniqueness for the new provider
    (provider="password") ride on the existing uq_provider_identity
    constraint on (provider, provider_sub); no new column or index needed
    for that.
    """
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('password_hash', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('password_hash')
