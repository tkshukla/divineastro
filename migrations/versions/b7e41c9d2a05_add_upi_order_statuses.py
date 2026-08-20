"""Add the UPI verification statuses to the orderstatus enum.

Production was created from an earlier revision of the initial migration, back
when an order could only be created / paid / failed / refunded. The manual UPI
flow later added two more states, but that was done by editing the initial
migration in place rather than adding a revision — so every database built from
scratch afterwards had all six values while the live one silently kept four.

Alembic reported itself at head throughout, because the version table said so.
The drift only surfaced at runtime: `Order.status == OrderStatus.awaiting_verification`
sends a label Postgres does not recognise, which fails the whole statement. That
took out `/api/admin/upi/pending` with a 500 and, with it, every manual payment
approval — the only way credits are ever granted.

Idempotent by design: `IF NOT EXISTS` means this is a no-op on the databases
that already have the values.

Revision ID: b7e41c9d2a05
Revises: ca114b6a6cbb
"""
from typing import Sequence, Union

from alembic import op

revision: str = "b7e41c9d2a05"
down_revision: Union[str, Sequence[str], None] = "ca114b6a6cbb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_VALUES = ("awaiting_verification", "rejected")


def upgrade() -> None:
    # Postgres only. SQLite has no enum type at all — it stores these as plain
    # text, so it already accepts every value and there is nothing to alter.
    # Development and the test suite run on SQLite, and an unguarded ALTER TYPE
    # would break startup there.
    if op.get_bind().dialect.name != "postgresql":
        return

    # ALTER TYPE ... ADD VALUE will not run inside a transaction block on older
    # servers, and even where it does the new label cannot be used until the
    # transaction commits. autocommit_block is alembic's supported escape.
    with op.get_context().autocommit_block():
        for value in NEW_VALUES:
            op.execute(
                f"ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS '{value}'"
            )


def downgrade() -> None:
    """Deliberately not implemented.

    Postgres cannot drop a value from an enum. Removing one means recreating the
    type and rewriting every dependent column, which would destroy any order
    currently sitting in that state — a customer's unverified payment. Refusing
    is safer than pretending to reverse it.
    """
    raise NotImplementedError(
        "orderstatus values cannot be removed without rebuilding the type "
        "and discarding orders that are in those states."
    )
