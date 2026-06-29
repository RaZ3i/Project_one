import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, apiFetch, LESSON_STATUS_LABELS, type Lesson, type Review, type Slot, type TutorDetail } from "../api/client";
import { useAuth } from "../api/auth";
import ProfileCard from "../components/ProfileCard";
import { RatingBadge, StarRating } from "../components/RatingDisplay";
import Avatar from "../components/Avatar";
import CancelLessonModal from "../components/CancelLessonModal";
import { CalendarIcon, UsersIcon, BookIcon } from "../components/icons";
import { formatDateTimeHHMM, formatTimeRange, isUpcomingLesson, lessonHasEnded } from "../utils/formatDate";

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string | number }) {
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

export default function TutorDashboard() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [startsAt, setStartsAt] = useState("");
  const [endsAt, setEndsAt] = useState("");
  const [slotError, setSlotError] = useState("");
  const [profileBio, setProfileBio] = useState("");
  const [profileSubjects, setProfileSubjects] = useState("");
  const [profileMeetingUrl, setProfileMeetingUrl] = useState("");
  const [profileSaved, setProfileSaved] = useState(false);

  const minDateTime = new Date().toISOString().slice(0, 16);

  const { data: profile } = useQuery({
    queryKey: ["my-tutor-profile"],
    queryFn: () => apiFetch<TutorDetail>(`/api/tutors/${user!.id}`),
    enabled: !!user,
  });

  const { data: reviews } = useQuery({
    queryKey: ["my-reviews", user?.id],
    queryFn: () => apiFetch<Review[]>(`/api/tutors/${user!.id}/reviews`),
    enabled: !!user,
  });

  useEffect(() => {
    if (profile) {
      setProfileBio(profile.bio ?? "");
      setProfileSubjects(profile.subjects ?? "");
      setProfileMeetingUrl(profile.default_meeting_url ?? "");
    }
  }, [profile]);

  const { data: slots } = useQuery({
    queryKey: ["my-slots"],
    queryFn: () => apiFetch<Slot[]>(`/api/slots?tutor_id=${user!.id}&available_only=false`),
    enabled: !!user,
  });

  const { data: lessons } = useQuery({
    queryKey: ["my-lessons"],
    queryFn: () => apiFetch<Lesson[]>("/api/lessons/me"),
  });

  const createSlot = useMutation({
    mutationFn: () =>
      apiFetch("/api/slots", {
        method: "POST",
        body: JSON.stringify({ starts_at: new Date(startsAt).toISOString(), ends_at: new Date(endsAt).toISOString() }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-slots"] });
      setStartsAt("");
      setEndsAt("");
      setSlotError("");
    },
    onError: (err) => setSlotError(err instanceof ApiError ? err.message : "Не удалось создать слот"),
  });

  const deleteSlot = useMutation({
    mutationFn: (id: string) => apiFetch(`/api/slots/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["my-slots"] }),
  });

  const updateProfile = useMutation({
    mutationFn: () =>
      apiFetch(`/api/tutors/me/profile`, {
        method: "PUT",
        body: JSON.stringify({
          bio: profileBio,
          subjects: profileSubjects,
          default_meeting_url: profileMeetingUrl || null,
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-tutor-profile"] });
      setProfileSaved(true);
      setTimeout(() => setProfileSaved(false), 2000);
    },
  });

  const handleCreateSlot = (e: FormEvent) => {
    e.preventDefault();
    if (!startsAt || !endsAt) return;
    const start = new Date(startsAt);
    const end = new Date(endsAt);
    if (start <= new Date() || end <= new Date()) {
      setSlotError("Слот должен быть в будущем");
      return;
    }
    createSlot.mutate();
  };

  const completedLessons = lessons?.filter((l) => l.status === "completed") ?? [];
  const uniqueStudents = new Set(completedLessons.map((l) => l.student_id)).size;
  const upcomingLessons = lessons?.filter((l) => isUpcomingLesson(l.status, l.slot_starts_at)) ?? [];

  return (
    <div className="space-y-8 sm:space-y-10">
      <h1 className="page-title">Кабинет репетитора</h1>

      <section>
        <h2 className="section-title">Профиль</h2>
        <ProfileCard />
      </section>

      <section>
        <h2 className="section-title">Статистика</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <StatCard icon={<UsersIcon className="w-8 h-8" />} label="Учеников" value={uniqueStudents} />
          <StatCard
            icon={<BookIcon className="w-8 h-8" />}
            label="Средняя оценка"
            value={profile?.avg_rating?.toFixed(1) ?? "—"}
          />
          <StatCard icon={<CalendarIcon className="w-8 h-8" />} label="Предстоящие" value={upcomingLessons.length} />
        </div>
      </section>

      {reviews && reviews.length > 0 && (
        <section>
          <h2 className="section-title">Отзывы</h2>
          <div className="card-surface mb-3">
            <RatingBadge avgRating={profile?.avg_rating ?? null} reviewCount={profile?.review_count ?? 0} />
          </div>
          <div className="space-y-3">
            {reviews.slice(0, 5).map((r) => (
              <div key={r.id} className="card-surface py-3">
                <div className="flex items-center gap-2 mb-1">
                  <StarRating rating={r.rating} />
                  <span className="text-sm font-medium">{r.student_name}</span>
                </div>
                {r.comment && <p className="text-sm text-muted">{r.comment}</p>}
              </div>
            ))}
          </div>
        </section>
      )}

      <section>
        <h2 className="section-title">Профиль репетитора</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            updateProfile.mutate();
          }}
          className="card-surface space-y-3 max-w-lg"
        >
          <div>
            <label className="block text-sm font-medium mb-1">Предметы</label>
            <input
              value={profileSubjects}
              onChange={(e) => setProfileSubjects(e.target.value)}
              className="form-input"
              placeholder="Математика, физика"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">О себе</label>
            <textarea
              value={profileBio}
              onChange={(e) => setProfileBio(e.target.value)}
              className="form-input min-h-[88px] py-2"
              rows={3}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Ссылка на встречу по умолчанию</label>
            <input
              value={profileMeetingUrl}
              onChange={(e) => setProfileMeetingUrl(e.target.value)}
              className="form-input"
              placeholder="https://zoom.us/j/..."
            />
          </div>
          <button type="submit" className="btn-primary text-sm">
            Сохранить профиль
          </button>
          {profileSaved && <span className="text-green-600 dark:text-green-400 text-sm ml-2">Сохранено!</span>}
        </form>
      </section>

      <section>
        <h2 className="section-title">Слоты доступности</h2>
        <form onSubmit={handleCreateSlot} className="card-surface space-y-3 max-w-lg mb-4">
          {slotError && <p className="text-red-600 text-sm">{slotError}</p>}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">Начало</label>
              <input
                type="datetime-local"
                required
                min={minDateTime}
                value={startsAt}
                onChange={(e) => setStartsAt(e.target.value)}
                className="form-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Окончание</label>
              <input
                type="datetime-local"
                required
                min={minDateTime}
                value={endsAt}
                onChange={(e) => setEndsAt(e.target.value)}
                className="form-input"
              />
            </div>
          </div>
          <button type="submit" disabled={createSlot.isPending} className="btn-primary text-sm">
            Добавить слот
          </button>
        </form>
        <div className="space-y-2">
          {slots?.map((slot) => (
            <div key={slot.id} className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 card-surface py-3">
              <span className="text-sm">
                {formatTimeRange(slot.starts_at, slot.ends_at)}
                {slot.is_booked && (
                  <span className="ml-2 text-xs bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300 px-2 py-0.5 rounded">занято</span>
                )}
              </span>
              {!slot.is_booked && (
                <button onClick={() => deleteSlot.mutate(slot.id)} className="btn-danger-text text-sm self-start sm:self-auto">
                  Удалить
                </button>
              )}
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="section-title">Мои занятия</h2>
        <div className="space-y-3">
          {lessons?.map((lesson) => (
            <TutorLessonCard key={lesson.id} lesson={lesson} />
          ))}
          {lessons?.length === 0 && <p className="text-muted">Пока нет занятий.</p>}
        </div>
      </section>
    </div>
  );
}

function TutorLessonCard({ lesson }: { lesson: Lesson }) {
  const queryClient = useQueryClient();
  const [meetingUrl, setMeetingUrl] = useState(lesson.meeting_url ?? "");
  const [showCancelModal, setShowCancelModal] = useState(false);

  const updateLesson = useMutation({
    mutationFn: (body: Record<string, string>) =>
      apiFetch(`/api/lessons/${lesson.id}`, { method: "PATCH", body: JSON.stringify(body) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-lessons"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread"] });
    },
  });

  const canComplete = lesson.status === "scheduled" && lessonHasEnded(lesson.slot_ends_at, lesson.slot_starts_at);
  const canCancel = lesson.status === "scheduled" && isUpcomingLesson(lesson.status, lesson.slot_starts_at);

  return (
    <>
      <div className="card-surface">
        <div className="flex items-center gap-3 mb-1">
          <Avatar name={lesson.student_name ?? "?"} size="sm" />
          <div>
            <p className="font-medium">{lesson.student_name}</p>
            <p className="text-sm text-muted">{lesson.subject}</p>
            <p className="text-sm text-muted">{formatDateTimeHHMM(lesson.slot_starts_at)}</p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2 mt-1">
          <span className="inline-block text-xs px-2 py-0.5 rounded bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300">
            {LESSON_STATUS_LABELS[lesson.status]}
          </span>
          <Link to={`/lessons/${lesson.id}`} className="text-primary text-xs hover:underline">
            Подробнее
          </Link>
        </div>
        {lesson.status === "scheduled" && (
          <div className="mt-3 flex flex-col sm:flex-row gap-2 sm:items-center">
            <input
              value={meetingUrl}
              onChange={(e) => setMeetingUrl(e.target.value)}
              placeholder="Ссылка на встречу для этого занятия"
              className="form-input text-sm flex-1 min-w-0"
            />
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => updateLesson.mutate({ meeting_url: meetingUrl })}
                className="touch-target text-primary text-sm hover:underline px-2"
              >
                Сохранить ссылку
              </button>
              {canCancel && (
                <button
                  onClick={() => setShowCancelModal(true)}
                  className="touch-target btn-danger-text text-sm px-2"
                >
                  Отменить
                </button>
              )}
              {canComplete && (
                <button
                  onClick={() => updateLesson.mutate({ status: "completed" })}
                  className="touch-target bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700"
                >
                  Завершить
                </button>
              )}
            </div>
          </div>
        )}
      </div>
      {showCancelModal && (
        <CancelLessonModal
          lessonId={lesson.id}
          onClose={() => setShowCancelModal(false)}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ["my-lessons"] });
            queryClient.invalidateQueries({ queryKey: ["notifications"] });
            queryClient.invalidateQueries({ queryKey: ["notifications-unread"] });
          }}
        />
      )}
    </>
  );
}
