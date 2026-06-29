"""Unit tests for lesson expansion: subjects, types, schemas."""

import sys
import unittest
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.subjects import parse_tutor_subjects, subject_allowed_for_tutor
from app.models.lesson import LessonType
from app.schemas.lesson import LessonCreate, LessonUpdate
from app.schemas.review import ReviewCreate
from app.services.booking import lesson_type_from_prior


class TutorSubjectsTests(unittest.TestCase):
    def test_parse_comma_separated_subjects(self):
        self.assertEqual(
            parse_tutor_subjects("Математика, Алгебра, Геометрия"),
            ["Математика", "Алгебра", "Геометрия"],
        )

    def test_subject_must_be_in_tutor_list(self):
        self.assertTrue(subject_allowed_for_tutor("Физика", "Физика, Математика"))
        self.assertFalse(subject_allowed_for_tutor("История", "Физика, Математика"))

    def test_empty_tutor_subjects_rejects_all(self):
        self.assertFalse(subject_allowed_for_tutor("Математика", None))
        self.assertEqual(parse_tutor_subjects(""), [])


class LessonTypeTests(unittest.TestCase):
    def test_first_lesson_is_trial(self):
        self.assertEqual(lesson_type_from_prior(False), LessonType.trial)

    def test_follow_up_is_regular(self):
        self.assertEqual(lesson_type_from_prior(True), LessonType.regular)


class ReviewSchemaTests(unittest.TestCase):
    def test_lesson_id_required(self):
        with self.assertRaises(ValidationError):
            ReviewCreate(tutor_id=uuid4(), rating=5)

    def test_valid_review_create(self):
        review = ReviewCreate(tutor_id=uuid4(), lesson_id=uuid4(), rating=4, comment="Отлично")
        self.assertEqual(review.rating, 4)


class LessonSchemaTests(unittest.TestCase):
    def test_lesson_create_requires_subject(self):
        with self.assertRaises(ValidationError):
            LessonCreate(slot_id=uuid4())

    def test_recording_url_must_be_http(self):
        with self.assertRaises(ValidationError):
            LessonUpdate(recording_url="ftp://example.com/video")

    def test_valid_recording_url(self):
        update = LessonUpdate(recording_url="https://youtube.com/watch?v=abc")
        self.assertEqual(update.recording_url, "https://youtube.com/watch?v=abc")


if __name__ == "__main__":
    unittest.main()
