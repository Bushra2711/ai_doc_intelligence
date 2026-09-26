"""baseline schema

Revision ID: 92c183c6664a
Revises:
Create Date: 2026-09-08 16:16:04.916653

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "92c183c6664a"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial DocuMind schema."""

    user_role = sa.Enum(
        "ADMIN",
        "EMPLOYEE",
        "AUDITOR",
        name="user_role",
    )
    document_status = sa.Enum(
        "PENDING",
        "UPLOADED",
        "PROCESSING",
        "COMPLETED",
        "FAILED",
        name="document_status",
    )

    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)
    document_status.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_is_active", "users", ["is_active"])

    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_type", sa.String(length=50), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("status", document_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_user_id", "documents", ["user_id"])

    op.create_table(
        "document_texts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id"),
    )
    op.create_index("ix_document_texts_document_id", "document_texts", ["document_id"])

    op.create_table(
        "document_analyses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("key_points", sa.Text(), nullable=False),
        sa.Column("important_information", sa.Text(), nullable=False),
        sa.Column("document_type", sa.String(length=100), nullable=False),
        sa.Column("invoice_number", sa.String(length=100), nullable=True),
        sa.Column("vendor", sa.String(length=255), nullable=True),
        sa.Column("invoice_date", sa.String(length=50), nullable=True),
        sa.Column("total_amount", sa.String(length=100), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("date_of_birth", sa.String(length=50), nullable=True),
        sa.Column("education", sa.Text(), nullable=True),
        sa.Column("skills", sa.Text(), nullable=True),
        sa.Column("experience", sa.Text(), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("height", sa.String(length=50), nullable=True),
        sa.Column("father_name", sa.String(length=255), nullable=True),
        sa.Column("father_occupation", sa.String(length=255), nullable=True),
        sa.Column("mother_occupation", sa.String(length=255), nullable=True),
        sa.Column("siblings", sa.String(length=255), nullable=True),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("effective_date", sa.String(length=50), nullable=True),
        sa.Column("expiry_date", sa.String(length=50), nullable=True),
        sa.Column("payment_terms", sa.Text(), nullable=True),
        sa.Column("signatures", sa.Text(), nullable=True),
        sa.Column("po_number", sa.String(length=100), nullable=True),
        sa.Column("supplier", sa.String(length=255), nullable=True),
        sa.Column("items", sa.Text(), nullable=True),
        sa.Column("amount", sa.String(length=100), nullable=True),
        sa.Column("delivery_date", sa.String(length=50), nullable=True),
        sa.Column("receipt_number", sa.String(length=100), nullable=True),
        sa.Column("receipt_date", sa.String(length=50), nullable=True),
        sa.Column("receipt_items", sa.Text(), nullable=True),
        sa.Column("receipt_amount", sa.String(length=100), nullable=True),
        sa.Column("receipt_tax", sa.String(length=100), nullable=True),
        sa.Column("policy_name", sa.String(length=255), nullable=True),
        sa.Column("policy_number", sa.String(length=100), nullable=True),
        sa.Column("policy_effective_date", sa.String(length=50), nullable=True),
        sa.Column("policy_expiry_date", sa.String(length=50), nullable=True),
        sa.Column("department", sa.String(length=255), nullable=True),
        sa.Column("sender", sa.String(length=255), nullable=True),
        sa.Column("receiver", sa.String(length=255), nullable=True),
        sa.Column("subject", sa.String(length=500), nullable=True),
        sa.Column("email_date", sa.String(length=50), nullable=True),
        sa.Column("email_purpose", sa.Text(), nullable=True),
        sa.Column("certificate_type", sa.String(length=255), nullable=True),
        sa.Column("institution", sa.String(length=255), nullable=True),
        sa.Column("issue_date", sa.String(length=50), nullable=True),
        sa.Column("certificate_number", sa.String(length=100), nullable=True),
        sa.Column("gst", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id"),
    )
    op.create_index("ix_document_analyses_document_id", "document_analyses", ["document_id"])


def downgrade() -> None:
    """Drop the initial DocuMind schema."""
    op.drop_index("ix_document_analyses_document_id", table_name="document_analyses")
    op.drop_table("document_analyses")
    op.drop_index("ix_document_texts_document_id", table_name="document_texts")
    op.drop_table("document_texts")
    op.drop_index("ix_documents_user_id", table_name="documents")
    op.drop_table("documents")
    op.drop_index("ix_users_is_active", table_name="users")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    sa.Enum(name="document_status").drop(bind, checkfirst=True)
    sa.Enum(name="user_role").drop(bind, checkfirst=True)
