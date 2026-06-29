"""Unit tests for lesson completion timing."""

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.booking import lesson_has_ended, lesson_end_time


def _lesson(*, starts_at: datetime, ends_at: datetime | None = None):
    slot = SimpleNamespace(starts_at=starts_at, ends_at=ends_at or starts_at + timedelta(hours=1))
    return SimpleNamespace(slot=slot)


class LessonEndTimeTests(unittest.TestCase):
    def test_lesson_not_ended_before_slot_end(self):
        now = datetime(2026, 6, 29, 14, 30, tzinfo=timezone.utc)
        lesson = _lesson(
            starts_at=datetime(2026, 6, 29, 14, 0, tzinfo=timezone.utc),
            ends_at=datetime(2026, 6, 29, 15, 0, tzinfo=timezone.utc),
        )
        self.assertFalse(lesson_has_ended(lesson, now=now))

    def test_lesson_ended_after_slot_end(self):
        now = datetime(2026, 6, 29, 15, 0, tzinfo=timezone.utc)
        lesson = _lesson(
            starts_at=datetime(2026, 6, 29, 14, 0, tzinfo=timezone.utc),
            ends_at=datetime(2026, 6, 29, 15, 0, tzinfo=timezone.utc),
        )
        self.assertTrue(lesson_has_ended(lesson, now=now))

    def test_uses_start_when_no_end(self):
        starts = datetime(2026, 6, 29, 10, 0, tzinfo=timezone.utc)
        lesson = _lesson(starts_at=starts, ends_at=starts)
        self.assertEqual(lesson_end_time(lesson), starts)


if __name__ == "__main__":
    unittest.main()
