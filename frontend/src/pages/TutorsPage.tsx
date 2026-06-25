import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { apiFetch, type TutorListItem } from "../api/client";

export default function TutorsPage() {
  const { data: tutors, isLoading, error } = useQuery({
    queryKey: ["tutors"],
    queryFn: () => apiFetch<TutorListItem[]>("/api/tutors"),
  });

  if (isLoading) return <p className="text-slate-500">Загрузка репетиторов...</p>;
  if (error) return <p className="text-red-600">Не удалось загрузить репетиторов</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Найти репетитора</h1>
      {tutors?.length === 0 ? (
        <p className="text-slate-500">Пока нет доступных репетиторов.</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {tutors?.map((tutor) => (
            <Link
              key={tutor.id}
              to={`/tutors/${tutor.id}`}
              className="block bg-white p-5 rounded-lg border hover:border-indigo-300 hover:shadow-sm transition"
            >
              <h2 className="text-lg font-semibold">{tutor.full_name}</h2>
              {tutor.subjects && (
                <p className="text-indigo-600 text-sm mt-1">{tutor.subjects}</p>
              )}
              {tutor.bio && <p className="text-slate-600 text-sm mt-2 line-clamp-2">{tutor.bio}</p>}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
