import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ApiError, apiFetch, getTutorBookingInfo, type Review, type Slot, type TutorDetail } from "../api/client";
import { useAuth } from "../api/auth";
import Avatar from "../components/Avatar";
import { RatingBadge, StarRating } from "../components/RatingDisplay";

function formatSlotTime(iso: string) {
  return new Date(iso).toLocaleString("ru-RU", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function parseSubjects(subjects: string | null): string[] {
  if (!subjects) return [];
  return subjects.split(",").map((s) => s.trim()).filter(Boolean);
}

function ReviewForm({ tutorId }: { tutorId: string }) {
  const queryClient = useQueryClient();
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [error, setError] = useState("");

  const mutation = useMutation({
    mutationFn: () =>
      apiFetch("/api/reviews", {
        method: "POST",
        body: JSON.stringify({
          tutor_id: tutorId,
          rating,
          comment: comment || null,
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tutor-reviews", tutorId] });
      queryClient.invalidateQueries({ queryKey: ["tutor", tutorId] });
      queryClient.invalidateQueries({ queryKey: ["tutor-booking-info", tutorId] });
      setError("");
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Не удалось отправить отзыв"),
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    mutation.mutate();
  };

  return (
    <form onSubmit={handleSubmit} className="card-surface space-y-3">
      <h3 className="font-medium">Оставить отзыв</h3>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <div>
        <label className="block text-sm font-medium mb-1">Оценка</label>
        <select value={rating} onChange={(e) => setRating(Number(e.target.value))} className="form-input">
          {[5, 4, 3, 2, 1].map((n) => (
            <option key={n} value={n}>
              {n} звёзд
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Комментарий</label>
        <textarea value={comment} onChange={(e) => setComment(e.target.value)} className="form-input py-2" rows={3} />
      </div>
      <button type="submit" disabled={mutation.isPending} className="btn-primary text-sm">
        Отправить отзыв
      </button>
    </form>
  );
}

export default function TutorDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState("");
  const [selectedSubject, setSelectedSubject] = useState("");
  const [pendingSlotId, setPendingSlotId] = useState<string | null>(null);

  const { data: tutor, isLoading } = useQuery({
    queryKey: ["tutor", id],
    queryFn: () => apiFetch<TutorDetail>(`/api/tutors/${id}`),
    enabled: !!id,
  });

  const { data: bookingInfo } = useQuery({
    queryKey: ["tutor-booking-info", id],
    queryFn: () => getTutorBookingInfo(id!),
    enabled: !!id && user?.role === "student",
  });

  const { data: reviews } = useQuery({
    queryKey: ["tutor-reviews", id],
    queryFn: () => apiFetch<Review[]>(`/api/tutors/${id}/reviews`),
    enabled: !!id,
  });

  const { data: slots } = useQuery({
    queryKey: ["slots", id],
    queryFn: () => apiFetch<Slot[]>(`/api/slots?tutor_id=${id}`),
    enabled: !!id,
  });

  const tutorSubjects = parseSubjects(tutor?.subjects ?? null);
  const availableSubjects = bookingInfo?.subjects.length ? bookingInfo.subjects : tutorSubjects;

  const bookMutation = useMutation({
    mutationFn: ({ slotId, subject }: { slotId: string; subject: string }) =>
      apiFetch("/api/lessons", { method: "POST", body: JSON.stringify({ slot_id: slotId, subject }) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["slots", id] });
      queryClient.invalidateQueries({ queryKey: ["tutor-booking-info", id] });
      setPendingSlotId(null);
      navigate("/dashboard");
    },
    onError: (err) => {
      setError(err instanceof ApiError ? err.message : "Не удалось забронировать");
      setPendingSlotId(null);
    },
  });

  const handleBook = (slotId: string) => {
    if (!user) {
      navigate("/login");
      return;
    }
    if (user.role !== "student") {
      setError("Только ученики могут бронировать занятия");
      return;
    }
    if (!selectedSubject) {
      setError("Выберите предмет для занятия");
      return;
    }
    setError("");
    setPendingSlotId(slotId);
    bookMutation.mutate({ slotId, subject: selectedSubject });
  };

  if (isLoading) return <p className="text-muted">Загрузка...</p>;
  if (!tutor) return <p className="text-red-600">Репетитор не найден</p>;

  return (
    <div>
      <Link to="/tutors" className="touch-target inline-flex items-center text-primary text-sm hover:underline -ml-2 px-2">
        &larr; Назад к репетиторам
      </Link>
      <div className="mt-4 card-surface">
        <div className="flex gap-4 items-start">
          <Avatar name={tutor.full_name} src={tutor.avatar_url} gender={tutor.gender} size="lg" />
          <div>
            <h1 className="text-xl sm:text-2xl font-bold">{tutor.full_name}</h1>
            <div className="mt-1">
              <RatingBadge avgRating={tutor.avg_rating} reviewCount={tutor.review_count} />
            </div>
            {tutor.subjects && <p className="text-primary mt-2">{tutor.subjects}</p>}
            {tutor.bio && <p className="text-muted mt-3 text-sm sm:text-base">{tutor.bio}</p>}
          </div>
        </div>
      </div>

      {reviews && reviews.length > 0 && (
        <section className="mt-6">
          <h2 className="section-title">Отзывы</h2>
          <div className="space-y-3">
            {reviews.map((r) => (
              <div key={r.id} className="card-surface py-3">
                <div className="flex items-center gap-2 mb-1">
                  <StarRating rating={r.rating} />
                  <span className="text-sm font-medium">{r.student_name}</span>
                  <span className="text-xs text-muted">
                    {new Date(r.created_at).toLocaleDateString("ru-RU")}
                  </span>
                </div>
                {r.comment && <p className="text-sm text-muted">{r.comment}</p>}
              </div>
            ))}
          </div>
        </section>
      )}

      {user?.role === "student" && bookingInfo?.can_review && id && (
        <section className="mt-6">
          <h2 className="section-title">Ваш отзыв</h2>
          <ReviewForm tutorId={id} />
        </section>
      )}

      {user?.role === "student" && bookingInfo?.has_reviewed && (
        <p className="text-muted text-sm mt-6">Вы уже оставили отзыв этому репетитору.</p>
      )}

      <h2 className="section-title mt-6 sm:mt-8">Доступные слоты</h2>
      {user?.role === "student" && bookingInfo && (
        <p
          className={`text-sm mb-3 inline-block px-2 py-1 rounded ${
            bookingInfo.is_trial
              ? "bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-200"
              : "bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-200"
          }`}
        >
          {bookingInfo.is_trial ? "Следующее занятие будет пробным" : "Следующее занятие будет повторным"}
        </p>
      )}
      {user?.role === "student" && availableSubjects.length > 0 && (
        <div className="mb-4 max-w-md">
          <label className="block text-sm font-medium mb-1">Предмет занятия</label>
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            className="form-input"
          >
            <option value="">Выберите предмет</option>
            {availableSubjects.map((subject) => (
              <option key={subject} value={subject}>
                {subject}
              </option>
            ))}
          </select>
        </div>
      )}
      {error && <p className="text-red-600 text-sm mb-3">{error}</p>}
      {slots?.length === 0 ? (
        <p className="text-muted">Нет доступных слотов. Загляните позже.</p>
      ) : (
        <div className="space-y-3">
          {slots?.map((slot) => (
            <div
              key={slot.id}
              className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 card-surface"
            >
              <span className="text-sm sm:text-base">
                {formatSlotTime(slot.starts_at)} – {formatSlotTime(slot.ends_at).split(", ").pop()}
              </span>
              <button
                onClick={() => handleBook(slot.id)}
                disabled={bookMutation.isPending && pendingSlotId === slot.id}
                className="btn-primary text-sm w-full sm:w-auto shrink-0"
              >
                Забронировать
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
