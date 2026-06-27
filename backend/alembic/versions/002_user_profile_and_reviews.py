"""user profile fields and reviews

Revision ID: 002
Revises: 001
Create Date: 2026-06-27

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_gender = postgresql.ENUM(
        "male", "female", "other", "prefer_not_say", name="user_gender", create_type=False
    )
    user_gender.create(op.get_bind(), checkfirst=True)

    op.add_column("users", sa.Column("gender", user_gender, nullable=True))
    op.add_column("users", sa.Column("birth_year", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("avatar_url", sa.String(length=500), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(length=50), nullable=True))
    op.add_column("users", sa.Column("city", sa.String(length=255), nullable=True))

    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tutor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tutor_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lesson_id", name="uq_reviews_lesson_id"),
        if_not_exists=True,
    )
    op.create_index(op.f("ix_reviews_student_id"), "reviews", ["student_id"], unique=False, if_not_exists=True)
    op.create_index(op.f("ix_reviews_tutor_id"), "reviews", ["tutor_id"], unique=False, if_not_exists=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_reviews_tutor_id"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_student_id"), table_name="reviews")
    op.drop_table("reviews")
    op.drop_column("users", "city")
    op.drop_column("users", "phone")
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "birth_year")
    op.drop_column("users", "gender")
    op.execute("DROP TYPE IF EXISTS user_gender")
