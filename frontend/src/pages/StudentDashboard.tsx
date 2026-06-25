import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch, type Lesson } from "../api/client";

function formatDate(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString();
}

function LessonCard({ lesson }: { lesson: Lesson }) {
  const queryClient = useQueryClient();
  const cancelMutation = useMutation({
    mutationFn: () =>
      apiFetch(`/api/lessons/${lesson.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: "cancelled" }),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["my-lessons"] }),
  });

  const isUpcoming = lesson.status === "scheduled" && lesson.slot_starts_at && new Date(lesson.slot_starts_at) > new Date();

  return (
    <div className="bg-white p-4 rounded-lg border">
      <div className="flex justify-between items-start">
        <div>
          <p className="font-medium">{lesson.tutor_name}</p>
          <p className="text-sm text-slate-500">{formatDate(lesson.slot_starts_at)}</p>
          <span
            className={`inline-block mt-2 text-xs px-2 py-0.5 rounded ${
              lesson.status === "scheduled"
                ? "bg-blue-100 text-blue-700"
                : lesson.status === "completed"
                  ? "bg-green-100 text-green-700"
                  : "bg-slate-100 text-slate-600"
            }`}
          >
            {lesson.status}
          </span>
        </div>
        <div className="flex flex-col gap-2 items-end">
          {lesson.effective_meeting_url && lesson.status === "scheduled" && (
            <a
              href={lesson.effective_meeting_url}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-green-600 text-white px-3 py-1.5 rounded text-sm hover:bg-green-700"
            >
              Join Meeting
            </a>
          )}
          {isUpcoming && (
            <button
              onClick={() => cancelMutation.mutate()}
              disabled={cancelMutation.isPending}
              className="text-red-600 text-sm hover:underline"
            >
              Cancel
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

  if (isLoading) return <p className="text-slate-500">Loading lessons...</p>;

  const upcoming = lessons?.filter(
    (l) => l.status === "scheduled" && l.slot_starts_at && new Date(l.slot_starts_at) > new Date()
  );
  const past = lessons?.filter(
    (l) => l.status !== "scheduled" || (l.slot_starts_at && new Date(l.slot_starts_at) <= new Date())
  );

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">My Lessons</h1>
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-3">Upcoming</h2>
        {upcoming?.length === 0 ? (
          <p className="text-slate-500">No upcoming lessons. <a href="/tutors" className="text-indigo-600 hover:underline">Browse tutors</a></p>
        ) : (
          <div className="space-y-3">{upcoming?.map((l) => <LessonCard key={l.id} lesson={l} />)}</div>
        )}
      </section>
      <section>
        <h2 className="text-lg font-semibold mb-3">Past & Cancelled</h2>
        {past?.length === 0 ? (
          <p className="text-slate-500">No past lessons yet.</p>
        ) : (
          <div className="space-y-3">{past?.map((l) => <LessonCard key={l.id} lesson={l} />)}</div>
        )}
      </section>
    </div>
  );
}
