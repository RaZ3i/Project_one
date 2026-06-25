import { Link } from "react-router-dom";
import { useAuth } from "../api/auth";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <div className="text-center py-16">
      <h1 className="text-4xl font-bold text-slate-900 mb-4">Платформа индивидуальных занятий</h1>
      <p className="text-lg text-slate-600 mb-8 max-w-xl mx-auto">
        Найдите опытных репетиторов, бронируйте свободные слоты и подключайтесь к урокам через Zoom или Google Meet.
      </p>
      <div className="flex gap-4 justify-center">
        <Link
          to="/tutors"
          className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700"
        >
          Смотреть репетиторов
        </Link>
        {!user && (
          <Link
            to="/register"
            className="border border-indigo-600 text-indigo-600 px-6 py-3 rounded-lg font-medium hover:bg-indigo-50"
          >
            Начать
          </Link>
        )}
      </div>
    </div>
  );
}
