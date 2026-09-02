"""Add Order.report_topic, for granular single-question paid reports.

A single-question report (e.g. "career", "marriage_timing") is a new SKU
kind, but there's nothing on `Order` recording *which* topic a given order
was for — `sku` alone doesn't carry that, since one sku maps to one fixed
topic in `billing.PRODUCTS` today but a future catalogue change (regional
variants, bundles) shouldn't have to re-derive the topic from the sku string.
Nullable and unused by every other product kind, so this is a pure additive
column — no backfill, no data migration.

Revision ID: d4a2f9c1e7b3
Revises: b7e41c9d2a05
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4a2f9c1e7b3"
down_revision: Union[str, Sequence[str], None] = "b7e41c9d2a05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("report_topic", sa.String(length=40), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "report_topic")
