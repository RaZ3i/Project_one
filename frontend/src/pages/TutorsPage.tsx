import { useQuery } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { useState } from "react";
import { apiFetch, type TutorListItem } from "../api/client";
import Avatar from "../components/Avatar";
import { RatingBadge } from "../components/RatingDisplay";
import { SearchIcon } from "../components/icons";

export default function TutorsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const subjectParam = searchParams.get("subject") ?? "";
  const [subjectInput, setSubjectInput] = useState(subjectParam);

  const { data: subjects } = useQuery({
    queryKey: ["subjects"],
    queryFn: () => apiFetch<string[]>("/api/subjects"),
  });

  const queryString = subjectParam ? `?subject=${encodeURIComponent(subjectParam)}` : "";
  const { data: tutors, isLoading, error } = useQuery({
    queryKey: ["tutors", subjectParam],
    queryFn: () => apiFetch<TutorListItem[]>(`/api/tutors${queryString}`),
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (subjectInput.trim()) {
      setSearchParams({ subject: subjectInput.trim() });
    } else {
      setSearchParams({});
    }
  };

  if (isLoading) return <p className="text-muted">Загрузка репетиторов...</p>;
  if (error) return <p className="text-red-600">Не удалось загрузить репетиторов</p>;

  return (
    <div>
      <h1 className="page-title">Найти репетитора</h1>

      <form onSubmit={handleSearch} className="card-surface mb-6 flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted" />
          <input
            value={subjectInput}
            onChange={(e) => setSubjectInput(e.target.value)}
            list="subjects-list"
            placeholder="Предмет: Математика, Физика..."
            className="form-input pl-10"
          />
          <datalist id="subjects-list">
            {subjects?.map((s) => (
              <option key={s} value={s} />
            ))}
          </datalist>
        </div>
        <button type="submit" className="btn-primary text-sm shrink-0">Искать</button>
        {subjectParam && (
          <button
            type="button"
            onClick={() => {
              setSubjectInput("");
              setSearchParams({});
            }}
            className="btn-secondary text-sm shrink-0"
          >
            Сбросить
          </button>
        )}
      </form>

      {subjectParam && (
        <p className="text-sm text-muted mb-4">
          Результаты по предмету: <span className="font-medium text-primary">{subjectParam}</span>
        </p>
      )}

      {tutors?.length === 0 ? (
        <p className="text-muted">Пока нет доступных репетиторов по этому запросу.</p>
      ) : (
        <div className="grid gap-3 sm:gap-4 grid-cols-1 md:grid-cols-2">
          {tutors?.map((tutor) => (
            <Link
              key={tutor.id}
              to={`/tutors/${tutor.id}`}
              className="block card-surface hover:border-primary-300 dark:hover:border-primary-600 transition min-h-[44px]"
            >
              <div className="flex gap-3">
                <Avatar name={tutor.full_name} src={tutor.avatar_url} size="md" />
                <div className="min-w-0 flex-1">
                  <h2 className="text-base sm:text-lg font-semibold">{tutor.full_name}</h2>
                  <div className="mt-1">
                    <RatingBadge avgRating={tutor.avg_rating} reviewCount={tutor.review_count} />
                  </div>
                  {tutor.subjects && (
                    <p className="text-primary text-sm mt-1">{tutor.subjects}</p>
                  )}
                  {tutor.bio && <p className="text-muted text-sm mt-2 line-clamp-2">{tutor.bio}</p>}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
