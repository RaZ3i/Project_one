"""lesson subject, type, recording_url

Revision ID: 004
Revises: 003
Create Date: 2026-06-27

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

lesson_type_enum = postgresql.ENUM("trial", "regular", name="lesson_type", create_type=False)


def upgrade() -> None:
    lesson_type_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "lessons",
        sa.Column("subject", sa.String(length=100), nullable=False, server_default="Математика"),
    )
    op.add_column(
        "lessons",
        sa.Column(
            "lesson_type",
            lesson_type_enum,
            nullable=False,
            server_default="regular",
        ),
    )
    op.add_column("lessons", sa.Column("recording_url", sa.String(length=500), nullable=True))
    op.alter_column("lessons", "subject", server_default=None)
    op.alter_column("lessons", "lesson_type", server_default=None)


def downgrade() -> None:
    op.drop_column("lessons", "recording_url")
    op.drop_column("lessons", "lesson_type")
    op.drop_column("lessons", "subject")
    op.execute("DROP TYPE IF EXISTS lesson_type")
