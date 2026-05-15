"""add users and organization memberships

Revision ID: 20260514_1838
Revises: None
Create Date: 2026-05-14 18:38:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260514_1838"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("clerk_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("current_org_id", sa.String(length=36), nullable=True),
        sa.Column("current_project_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["current_org_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["current_project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_clerk_id"), "users", ["clerk_id"], unique=True)
    op.create_index(op.f("ix_users_current_org_id"), "users", ["current_org_id"], unique=False)
    op.create_index(op.f("ix_users_current_project_id"), "users", ["current_project_id"], unique=False)

    op.create_table(
        "organization_memberships",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "organization_id", name="uq_user_org_membership"),
    )
    op.create_index(
        op.f("ix_organization_memberships_id"),
        "organization_memberships",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_memberships_user_id"),
        "organization_memberships",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_memberships_organization_id"),
        "organization_memberships",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_organization_memberships_organization_id"), table_name="organization_memberships")
    op.drop_index(op.f("ix_organization_memberships_user_id"), table_name="organization_memberships")
    op.drop_index(op.f("ix_organization_memberships_id"), table_name="organization_memberships")
    op.drop_table("organization_memberships")
    op.drop_index(op.f("ix_users_current_project_id"), table_name="users")
    op.drop_index(op.f("ix_users_current_org_id"), table_name="users")
    op.drop_index(op.f("ix_users_clerk_id"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
