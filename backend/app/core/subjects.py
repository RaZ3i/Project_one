"""Standard school subjects (Russian curriculum)."""

SUBJECTS: list[str] = [
    "Математика",
    "Русский язык",
    "Физика",
    "Химия",
    "Биология",
    "История",
    "Обществознание",
    "Английский язык",
    "Информатика",
    "География",
    "Литература",
    "Алгебра",
    "Геометрия",
    "Немецкий язык",
    "Французский язык",
]


def parse_tutor_subjects(subjects_str: str | None) -> list[str]:
    if not subjects_str:
        return []
    return [part.strip() for part in subjects_str.split(",") if part.strip()]


def subject_allowed_for_tutor(subject: str, tutor_subjects: str | None) -> bool:
    allowed = parse_tutor_subjects(tutor_subjects)
    if not allowed:
        return False
    return subject in allowed
