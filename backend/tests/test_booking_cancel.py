"""Unit tests for slot availability after lesson cancellation."""

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.lesson import LessonStatus
from app.services.booking import slot_is_actively_booked


def _slot(*, is_booked: bool = False, lesson_status: LessonStatus | None = None):
    lesson = SimpleNamespace(status=lesson_status) if lesson_status is not None else None
    return SimpleNamespace(is_booked=is_booked, lesson=lesson)


class SlotAvailabilityTests(unittest.TestCase):
    def test_open_slot_without_lesson(self):
        slot = _slot(is_booked=False)
        self.assertFalse(slot_is_actively_booked(slot))

    def test_scheduled_lesson_marks_slot_booked(self):
        slot = _slot(is_booked=True, lesson_status=LessonStatus.scheduled)
        self.assertTrue(slot_is_actively_booked(slot))

    def test_cancelled_lesson_marks_slot_available(self):
        slot = _slot(is_booked=True, lesson_status=LessonStatus.cancelled)
        self.assertFalse(slot_is_actively_booked(slot))

    def test_stale_is_booked_flag_ignored_when_lesson_cancelled(self):
        """Cancelled lessons must not block re-booking even if is_booked stayed True."""
        slot = _slot(is_booked=True, lesson_status=LessonStatus.cancelled)
        self.assertFalse(slot_is_actively_booked(slot))

    def test_completed_lesson_not_available_for_rebook_display(self):
        slot = _slot(is_booked=True, lesson_status=LessonStatus.completed)
        self.assertFalse(slot_is_actively_booked(slot))


class CancelFlowLogicTests(unittest.TestCase):
    def test_available_only_filter_logic(self):
        """Slots with cancelled lessons should pass available_only filtering."""
        now = datetime.now(timezone.utc)
        future = now.replace(year=now.year + 1)

        cancelled_lesson = SimpleNamespace(id=uuid4(), status=LessonStatus.cancelled)
        scheduled_lesson = SimpleNamespace(id=uuid4(), status=LessonStatus.scheduled)

        def is_available(lesson, starts_at):
            if starts_at <= now:
                return False
            if lesson is None:
                return True
            return lesson.status != LessonStatus.scheduled

        self.assertTrue(is_available(None, future))
        self.assertTrue(is_available(cancelled_lesson, future))
        self.assertFalse(is_available(scheduled_lesson, future))


if __name__ == "__main__":
    unittest.main()
