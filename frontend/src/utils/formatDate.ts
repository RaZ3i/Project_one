const LOCALE = "ru-RU";

const DATE_TIME_OPTS: Intl.DateTimeFormatOptions = {
  year: "numeric",
  month: "short",
  day: "numeric",
  hour: "2-digit",
  minute: "2-digit",
};

const TIME_OPTS: Intl.DateTimeFormatOptions = {
  hour: "2-digit",
  minute: "2-digit",
};

export function formatDateTimeHHMM(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString(LOCALE, DATE_TIME_OPTS);
}

export function formatTimeHHMM(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleTimeString(LOCALE, TIME_OPTS);
}

export function formatTimeRange(starts: string | null | undefined, ends: string | null | undefined): string {
  if (!starts) return "—";
  const start = formatDateTimeHHMM(starts);
  if (!ends) return start;
  return `${start} – ${formatTimeHHMM(ends)}`;
}

export function lessonHasEnded(slotEndsAt: string | null | undefined, slotStartsAt?: string | null): boolean {
  const endIso = slotEndsAt ?? slotStartsAt;
  if (!endIso) return false;
  return new Date(endIso) <= new Date();
}

export function isUpcomingLesson(
  status: string,
  slotStartsAt: string | null | undefined
): boolean {
  return status === "scheduled" && !!slotStartsAt && new Date(slotStartsAt) > new Date();
}
