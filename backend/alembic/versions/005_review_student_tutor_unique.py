"""review unique per student-tutor pair

Revision ID: 005
Revises: 004
Create Date: 2026-06-29

"""
from typing import Sequence, Union

from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("uq_reviews_lesson_id", "reviews", type_="unique")
    op.create_unique_constraint("uq_reviews_student_tutor", "reviews", ["student_id", "tutor_id"])


def downgrade() -> None:
    op.drop_constraint("uq_reviews_student_tutor", "reviews", type_="unique")
    op.create_unique_constraint("uq_reviews_lesson_id", "reviews", ["lesson_id"])
