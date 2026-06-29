"""Validate seed demo data invariants without a database."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.subjects import subject_allowed_for_tutor, parse_tutor_subjects
from app.models.lesson import LessonStatus
from scripts.seed import EXTRA_LESSONS_DATA, REVIEWS_DATA, STUDENTS, TUTORS, tutor_subject


class SeedDataTests(unittest.TestCase):
    def test_review_pairs_are_unique(self):
        pairs = [(s, t) for s, t, *_ in REVIEWS_DATA]
        self.assertEqual(len(pairs), len(set(pairs)), "Each student-tutor pair may have only one review")

    def test_review_indices_in_range(self):
        for student_idx, tutor_idx, rating, _comment in REVIEWS_DATA:
            self.assertLess(student_idx, len(STUDENTS))
            self.assertLess(tutor_idx, len(TUTORS))
            self.assertGreaterEqual(rating, 1)
            self.assertLessEqual(rating, 5)

    def test_extra_lesson_indices_in_range(self):
        for student_idx, tutor_idx, status, _days, subject_idx, _recording in EXTRA_LESSONS_DATA:
            self.assertLess(student_idx, len(STUDENTS))
            self.assertLess(tutor_idx, len(TUTORS))
            self.assertIsInstance(status, LessonStatus)
            subjects = parse_tutor_subjects(TUTORS[tutor_idx]["subjects"])
            if subjects:
                self.assertLess(subject_idx, len(subjects))

    def test_lesson_subjects_match_tutor_profile(self):
        for tutor_idx in range(len(TUTORS)):
            subject = tutor_subject(tutor_idx, 0)
            self.assertTrue(
                subject_allowed_for_tutor(subject, TUTORS[tutor_idx]["subjects"]),
                f"Subject {subject!r} not allowed for tutor {tutor_idx}",
            )

    def test_demo_student_has_regular_follow_up_with_anna(self):
        """student@example.com: trial review with tutor 0, then regular lessons in EXTRA."""
        maria_anna = [(s, t, st) for s, t, st, *_ in EXTRA_LESSONS_DATA if s == 0 and t == 0]
        statuses = [st for _s, _t, st, *_ in maria_anna]
        self.assertIn(LessonStatus.completed, statuses)
        self.assertIn(LessonStatus.scheduled, statuses)
        self.assertIn((0, 0), [(s, t) for s, t, *_ in REVIEWS_DATA])


if __name__ == "__main__":
    unittest.main()
