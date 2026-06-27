"""restrict user gender to male/female

Revision ID: 003
Revises: 002
Create Date: 2026-06-27

"""
from typing import Sequence, Union

from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE users SET gender = NULL WHERE gender IN ('other', 'prefer_not_say')")
    op.execute("ALTER TYPE user_gender RENAME TO user_gender_old")
    op.execute("CREATE TYPE user_gender AS ENUM ('male', 'female')")
    op.execute(
        "ALTER TABLE users ALTER COLUMN gender TYPE user_gender "
        "USING gender::text::user_gender"
    )
    op.execute("DROP TYPE user_gender_old")


def downgrade() -> None:
    op.execute("ALTER TYPE user_gender RENAME TO user_gender_new")
    op.execute("CREATE TYPE user_gender AS ENUM ('male', 'female', 'other', 'prefer_not_say')")
    op.execute(
        "ALTER TABLE users ALTER COLUMN gender TYPE user_gender "
        "USING gender::text::user_gender"
    )
    op.execute("DROP TYPE user_gender_new")
