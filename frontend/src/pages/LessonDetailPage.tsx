import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  ApiError,
  apiFetch,
  getLesson,
  LESSON_STATUS_LABELS,
  LESSON_TYPE_LABELS,
  type Lesson,
} from "../api/client";
import { useAuth } from "../api/auth";
import Avatar from "../components/Avatar";
import CancelLessonModal from "../components/CancelLessonModal";
import { formatTimeRange, isUpcomingLesson, lessonHasEnded } from "../utils/formatDate";

function RecordingUrlForm({ lesson }: { lesson: Lesson }) {
  const queryClient = useQueryClient();
  const [recordingUrl, setRecordingUrl] = useState(lesson.recording_url ?? "");
  const [error, setError] = useState("");

  const mutation = useMutation({
    mutationFn: () =>
      apiFetch(`/api/lessons/${lesson.id}`, {
        method: "PATCH",
        body: JSON.stringify({ recording_url: recordingUrl || null }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lesson", lesson.id] });
      queryClient.invalidateQueries({ queryKey: ["my-lessons"] });
      setError("");
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Не удалось сохранить ссылку"),
  });

  return (
    <div className="card-surface space-y-3">
      <h3 className="font-medium">Ссылка на запись урока</h3>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <input
        value={recordingUrl}
        onChange={(e) => setRecordingUrl(e.target.value)}
        placeholder="https://youtube.com/watch?v=..."
        className="form-input text-sm"
      />
      <button
        type="button"
        onClick={() => mutation.mutate()}
        disabled={mutation.isPending}
        className="btn-primary text-sm"
      >
        Сохранить запись
      </button>
    </div>
  );
}

export default function LessonDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showCancelModal, setShowCancelModal] = useState(false);

  const { data: lesson, isLoading, error } = useQuery({
    queryKey: ["lesson", id],
    queryFn: () => getLesson(id!),
    enabled: !!id,
  });

  const cancelMutation = useMutation({
    mutationFn: () =>
      apiFetch(`/api/lessons/${id}`, { method: "PATCH", body: JSON.stringify({ status: "cancelled" }) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lesson", id] });
      queryClient.invalidateQueries({ queryKey: ["my-lessons"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread"] });
    },
  });

  const completeMutation = useMutation({
    mutationFn: () =>
      apiFetch(`/api/lessons/${id}`, { method: "PATCH", body: JSON.stringify({ status: "completed" }) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lesson", id] });
      queryClient.invalidateQueries({ queryKey: ["my-lessons"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread"] });
    },
  });

  if (isLoading) return <p className="text-muted">Загрузка...</p>;
  if (error || !lesson) {
    return (
      <div>
        <p className="text-red-600">Занятие не найдено или нет доступа.</p>
        <button onClick={() => navigate(-1)} className="text-primary text-sm mt-2 hover:underline">
          Назад
        </button>
      </div>
    );
  }

  const isStudent = user?.role === "student";
  const isTutor = user?.role === "tutor";
  const counterpartName = isStudent ? lesson.tutor_name : lesson.student_name;
  const counterpartAvatar = isStudent ? lesson.tutor_avatar_url : lesson.student_avatar_url;
  const counterpartGender = isStudent ? lesson.tutor_gender : lesson.student_gender;
  const isUpcoming = isUpcomingLesson(lesson.status, lesson.slot_starts_at);
  const canComplete = isTutor && lesson.status === "scheduled" && lessonHasEnded(lesson.slot_ends_at, lesson.slot_starts_at);
  const canTutorCancel = isTutor && isUpcoming;
  const dashboardPath = isTutor ? "/tutor/dashboard" : "/dashboard";

  return (
    <div className="space-y-6 max-w-2xl">
      <Link to={dashboardPath} className="touch-target inline-flex items-center text-primary text-sm hover:underline -ml-2 px-2">
        &larr; Назад в кабинет
      </Link>

      <div className="card-surface space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <h1 className="text-xl sm:text-2xl font-bold">Занятие</h1>
          <span
            className={`text-xs px-2 py-0.5 rounded ${
              lesson.lesson_type === "trial"
                ? "bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-200"
                : "bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-200"
            }`}
          >
            {LESSON_TYPE_LABELS[lesson.lesson_type]}
          </span>
          <span
            className={`text-xs px-2 py-0.5 rounded ${
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

        <div>
          <p className="text-sm text-muted">Предмет</p>
          <p className="font-medium">{lesson.subject}</p>
        </div>

        <div>
          <p className="text-sm text-muted">Время</p>
          <p className="font-medium">{formatTimeRange(lesson.slot_starts_at, lesson.slot_ends_at)}</p>
        </div>

        {lesson.status === "cancelled" && lesson.cancellation_reason && (
          <div>
            <p className="text-sm text-muted">Причина отмены</p>
            <p className="font-medium text-amber-700 dark:text-amber-300">{lesson.cancellation_reason}</p>
          </div>
        )}

        <div className="flex items-center gap-3">
          <Avatar name={counterpartName ?? "?"} src={counterpartAvatar} gender={counterpartGender} size="md" />
          <div>
            <p className="text-sm text-muted">{isStudent ? "Репетитор" : "Ученик"}</p>
            <p className="font-medium">{counterpartName}</p>
          </div>
        </div>

        {lesson.effective_meeting_url && lesson.status === "scheduled" && (
          <a
            href={lesson.effective_meeting_url}
            target="_blank"
            rel="noopener noreferrer"
            className="touch-target inline-flex items-center justify-center bg-green-600 text-white px-4 py-2 rounded-md text-sm hover:bg-green-700"
          >
            Присоединиться к встрече
          </a>
        )}

        {lesson.recording_url && (
          <div>
            <p className="text-sm text-muted mb-1">Запись урока</p>
            <a
              href={lesson.recording_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline text-sm"
            >
              Смотреть запись
            </a>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {isStudent && isUpcoming && (
            <button
              onClick={() => cancelMutation.mutate()}
              disabled={cancelMutation.isPending}
              className="btn-danger-text text-sm"
            >
              Отменить занятие
            </button>
          )}

          {canTutorCancel && (
            <button
              onClick={() => setShowCancelModal(true)}
              className="btn-danger-text text-sm"
            >
              Отменить занятие
            </button>
          )}

          {canComplete && (
            <button
              onClick={() => completeMutation.mutate()}
              disabled={completeMutation.isPending}
              className="btn-primary text-sm"
            >
              Завершить урок
            </button>
          )}
        </div>
      </div>

      {isTutor && lesson.status === "completed" && <RecordingUrlForm lesson={lesson} />}

      {showCancelModal && id && (
        <CancelLessonModal
          lessonId={id}
          onClose={() => setShowCancelModal(false)}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ["lesson", id] });
            queryClient.invalidateQueries({ queryKey: ["my-lessons"] });
            queryClient.invalidateQueries({ queryKey: ["notifications"] });
            queryClient.invalidateQueries({ queryKey: ["notifications-unread"] });
          }}
        />
      )}
    </div>
  );
}
