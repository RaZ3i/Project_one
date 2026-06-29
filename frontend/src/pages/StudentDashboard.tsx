import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { apiFetch, LESSON_STATUS_LABELS, type Lesson } from "../api/client";
import ProfileCard from "../components/ProfileCard";
import { BookIcon, CalendarIcon } from "../components/icons";
import { formatDateTimeHHMM, isUpcomingLesson } from "../utils/formatDate";

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div className="card-surface flex items-center gap-3">
      <div className="text-primary">{icon}</div>
      <div>
        <p className="text-2xl font-bold">{value}</p>
        <p className="text-sm text-muted">{label}</p>
      </div>
    </div>
  );
}

function LessonCard({ lesson }: { lesson: Lesson }) {
  const queryClient = useQueryClient();
  const cancelMutation = useMutation({
    mutationFn: () =>
      apiFetch(`/api/lessons/${lesson.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: "cancelled" }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-lessons"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread"] });
    },
  });

  const isUpcoming = isUpcomingLesson(lesson.status, lesson.slot_starts_at);

  return (
    <div className="card-surface">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3">
        <div>
          <p className="font-medium">{lesson.tutor_name}</p>
          <p className="text-sm text-muted">{lesson.subject}</p>
          <p className="text-sm text-muted">{formatDateTimeHHMM(lesson.slot_starts_at)}</p>
          {lesson.status === "cancelled" && lesson.cancellation_reason && (
            <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
              Причина отмены: {lesson.cancellation_reason}
            </p>
          )}
          <span
            className={`inline-block mt-2 text-xs px-2 py-0.5 rounded ${
              lesson.status === "scheduled"
                ? "bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300"
                : lesson.status === "completed"
                  ? "bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300"
                  : "bg-secondary-100 dark:bg-secondary-700 text-secondary-600 dark:text-secondary-300"
            }`}
          >
            {LESSON_STATUS_LABELS[lesson.status]}
          </span>
        </div>
        <div className="flex flex-row sm:flex-col gap-2 sm:items-end">
          <Link to={`/lessons/${lesson.id}`} className="text-primary text-sm hover:underline">
            Подробнее
          </Link>
          {lesson.effective_meeting_url && lesson.status === "scheduled" && (
            <a
              href={lesson.effective_meeting_url}
              target="_blank"
              rel="noopener noreferrer"
              className="touch-target inline-flex items-center justify-center bg-green-600 text-white px-4 py-2 rounded-md text-sm hover:bg-green-700"
            >
              Присоединиться
            </a>
          )}
          {isUpcoming && (
            <button
              onClick={() => cancelMutation.mutate()}
              disabled={cancelMutation.isPending}
              className="btn-danger-text text-sm"
            >
              Отменить
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default function StudentDashboard() {
  const { data: lessons, isLoading } = useQuery({
    queryKey: ["my-lessons"],
    queryFn: () => apiFetch<Lesson[]>("/api/lessons/me"),
  });

  if (isLoading) return <p className="text-muted">Загрузка...</p>;

  const upcoming = lessons?.filter((l) => isUpcomingLesson(l.status, l.slot_starts_at)) ?? [];
  const completed = lessons?.filter((l) => l.status === "completed") ?? [];
  const past = lessons?.filter(
    (l) => l.status !== "scheduled" || (l.slot_starts_at && new Date(l.slot_starts_at) <= new Date())
  ) ?? [];

  return (
    <div className="space-y-8">
      <h1 className="page-title">Личный кабинет</h1>

      <section>
        <h2 className="section-title">Профиль</h2>
        <ProfileCard />
      </section>

      <section>
        <h2 className="section-title">Статистика</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <StatCard icon={<BookIcon className="w-8 h-8" />} label="Всего занятий" value={lessons?.length ?? 0} />
          <StatCard icon={<CalendarIcon className="w-8 h-8" />} label="Предстоящие" value={upcoming.length} />
          <StatCard icon={<BookIcon className="w-8 h-8" />} label="Завершённые" value={completed.length} />
        </div>
      </section>

      <section>
        <h2 className="section-title">Быстрые ссылки</h2>
        <div className="flex flex-wrap gap-3">
          <Link to="/tutors" className="btn-primary text-sm">Найти репетитора</Link>
          <Link to="/tutors?subject=Математика" className="btn-secondary text-sm">Математика</Link>
          <Link to="/tutors?subject=Английский язык" className="btn-secondary text-sm">Английский</Link>
        </div>
      </section>

      <section>
        <h2 className="section-title">Предстоящие занятия</h2>
        {upcoming.length === 0 ? (
          <p className="text-muted">
            Нет предстоящих занятий.{" "}
            <Link to="/tutors" className="text-primary hover:underline">
              Смотреть репетиторов
            </Link>
          </p>
        ) : (
          <div className="space-y-3">{upcoming.map((l) => <LessonCard key={l.id} lesson={l} />)}</div>
        )}
      </section>

      <section>
        <h2 className="section-title">Прошедшие и отменённые</h2>
        {past.length === 0 ? (
          <p className="text-muted">Пока нет прошедших занятий.</p>
        ) : (
          <div className="space-y-3">{past.map((l) => <LessonCard key={l.id} lesson={l} />)}</div>
        )}
      </section>
    </div>
  );
}
