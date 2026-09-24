"""add ingestion source metadata

Revision ID: d4e7a91b2c10
Revises: c81a7d4e2f10
Create Date: 2026-09-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d4e7a91b2c10"
down_revision: Union[str, Sequence[str], None] = "c81a7d4e2f10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("ingestion_source", sa.String(length=32), nullable=False, server_default="portal"),
    )
    op.create_index(
        "ix_documents_ingestion_source",
        "documents",
        ["ingestion_source"],
    )


def downgrade() -> None:
    op.drop_index("ix_documents_ingestion_source", table_name="documents")
    op.drop_column("documents", "ingestion_source")
