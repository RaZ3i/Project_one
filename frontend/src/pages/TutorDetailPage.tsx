import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ApiError, apiFetch, type Slot, type TutorDetail } from "../api/client";
import { useAuth } from "../api/auth";

function formatSlotTime(iso: string) {
  return new Date(iso).toLocaleString("ru-RU", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function TutorDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState("");

  const { data: tutor, isLoading } = useQuery({
    queryKey: ["tutor", id],
    queryFn: () => apiFetch<TutorDetail>(`/api/tutors/${id}`),
    enabled: !!id,
  });

  const { data: slots } = useQuery({
    queryKey: ["slots", id],
    queryFn: () => apiFetch<Slot[]>(`/api/slots?tutor_id=${id}`),
    enabled: !!id,
  });

  const bookMutation = useMutation({
    mutationFn: (slotId: string) =>
      apiFetch("/api/lessons", { method: "POST", body: JSON.stringify({ slot_id: slotId }) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["slots", id] });
      navigate("/dashboard");
    },
    onError: (err) => {
      setError(err instanceof ApiError ? err.message : "Не удалось забронировать");
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
    setError("");
    bookMutation.mutate(slotId);
  };

  if (isLoading) return <p className="text-slate-500">Загрузка...</p>;
  if (!tutor) return <p className="text-red-600">Репетитор не найден</p>;

  return (
    <div>
      <Link to="/tutors" className="text-indigo-600 text-sm hover:underline">
        &larr; Назад к репетиторам
      </Link>
      <div className="mt-4 bg-white p-6 rounded-lg border">
        <h1 className="text-2xl font-bold">{tutor.full_name}</h1>
        {tutor.subjects && <p className="text-indigo-600 mt-1">{tutor.subjects}</p>}
        {tutor.bio && <p className="text-slate-600 mt-3">{tutor.bio}</p>}
      </div>

      <h2 className="text-xl font-semibold mt-8 mb-4">Доступные слоты</h2>
      {error && <p className="text-red-600 text-sm mb-3">{error}</p>}
      {slots?.length === 0 ? (
        <p className="text-slate-500">Нет доступных слотов. Загляните позже.</p>
      ) : (
        <div className="space-y-3">
          {slots?.map((slot) => (
            <div
              key={slot.id}
              className="flex items-center justify-between bg-white p-4 rounded-lg border"
            >
              <span>{formatSlotTime(slot.starts_at)} – {formatSlotTime(slot.ends_at).split(", ").pop()}</span>
              <button
                onClick={() => handleBook(slot.id)}
                disabled={bookMutation.isPending}
                className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm hover:bg-indigo-700 disabled:opacity-50"
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
