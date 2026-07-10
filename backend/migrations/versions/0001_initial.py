"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-08
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def uuid_pk():
    return sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()"))

def audit_cols():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    ]

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.create_table("users", uuid_pk(), sa.Column("email", sa.String(255), nullable=False, unique=True), sa.Column("full_name", sa.String(160), nullable=False), sa.Column("role", sa.String(40), server_default="rep", nullable=False), sa.Column("hashed_password", sa.String(255), nullable=False), sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False), *audit_cols())

    op.create_table(
        "refresh_tokens",
        uuid_pk(),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token", sa.String(160), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        *audit_cols(),
    )
    op.create_index(
        "ix_refresh_tokens_user_id",
        "refresh_tokens",
        ["user_id"],
    )
    op.create_index(
        "ix_refresh_tokens_token",
        "refresh_tokens",
        ["token"],
        unique=True,
    )
    op.create_index(
        "ix_refresh_tokens_expires_at",
        "refresh_tokens",
        ["expires_at"],
    )

    op.create_table("hcps", uuid_pk(), sa.Column("owner_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=False), sa.Column("name", sa.String(160), nullable=False), sa.Column("specialty", sa.String(120), nullable=False), sa.Column("institution", sa.String(180), nullable=True), sa.Column("city", sa.String(120), nullable=True), sa.Column("email", sa.String(255), nullable=True), sa.Column("phone", sa.String(80), nullable=True), sa.Column("sentiment_score", sa.Float(), server_default="0.5", nullable=False), sa.Column("last_contacted_at", sa.DateTime(timezone=True), nullable=True), *audit_cols())
    op.create_index("ix_hcps_owner_name", "hcps", ["owner_id", "name"])
    op.create_table("products", uuid_pk(), sa.Column("name", sa.String(160), nullable=False, unique=True), sa.Column("therapy_area", sa.String(120), nullable=True), sa.Column("description", sa.Text(), nullable=True), *audit_cols())
    op.create_table("materials", uuid_pk(), sa.Column("name", sa.String(160), nullable=False), sa.Column("material_type", sa.String(80), nullable=False), sa.Column("url", sa.String(500), nullable=True), *audit_cols())
    op.create_table("samples", uuid_pk(), sa.Column("product_id", sa.UUID(), sa.ForeignKey("products.id"), nullable=False), sa.Column("lot_number", sa.String(80), nullable=True), sa.Column("quantity_available", sa.Integer(), server_default="0", nullable=False), *audit_cols())
    op.create_table("interactions", uuid_pk(), sa.Column("owner_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=False), sa.Column("hcp_id", sa.UUID(), sa.ForeignKey("hcps.id"), nullable=False), sa.Column("interaction_type", sa.String(80), nullable=False), sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False), sa.Column("attendees", sa.JSON(), nullable=False), sa.Column("topics_discussed", sa.JSON(), nullable=False), sa.Column("materials_shared", sa.JSON(), nullable=False), sa.Column("samples_distributed", sa.JSON(), nullable=False), sa.Column("observed_sentiment", sa.String(40), nullable=False), sa.Column("outcome", sa.Text(), nullable=False), sa.Column("follow_up_action", sa.Text(), nullable=True), sa.Column("summary", sa.Text(), nullable=False), *audit_cols())
    op.create_index("ix_interactions_owner_date", "interactions", ["owner_id", "occurred_at"])
    op.create_table("follow_ups", uuid_pk(), sa.Column("interaction_id", sa.UUID(), sa.ForeignKey("interactions.id"), nullable=False), sa.Column("owner_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=False), sa.Column("hcp_id", sa.UUID(), sa.ForeignKey("hcps.id"), nullable=False), sa.Column("due_at", sa.DateTime(timezone=True), nullable=True), sa.Column("priority", sa.String(20), server_default="medium", nullable=False), sa.Column("status", sa.String(30), server_default="pending", nullable=False), sa.Column("action", sa.Text(), nullable=False), *audit_cols())
    op.create_table("interaction_history", uuid_pk(), sa.Column("interaction_id", sa.UUID(), sa.ForeignKey("interactions.id"), nullable=False), sa.Column("actor_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=False), sa.Column("event_type", sa.String(80), nullable=False), sa.Column("payload", sa.JSON(), nullable=False), *audit_cols())
    op.create_table("audit_logs", uuid_pk(), sa.Column("actor_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=True), sa.Column("entity_type", sa.String(80), nullable=False), sa.Column("entity_id", sa.UUID(), nullable=True), sa.Column("action", sa.String(80), nullable=False), sa.Column("metadata", sa.JSON(), nullable=False), *audit_cols())

def downgrade():
    op.drop_index("ix_refresh_tokens_expires_at", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_token", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    for table in [
        "audit_logs",
        "interaction_history",
        "follow_ups",
        "interactions",
        "samples",
        "materials",
        "products",
        "hcps",
        "users",
    ]:
        op.drop_table(table)