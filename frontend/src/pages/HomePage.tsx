import { Link } from "react-router-dom";
import { useAuth } from "../api/auth";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <div className="text-center py-10 sm:py-16 px-2">
      <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-4 leading-tight">
        Платформа индивидуальных занятий
      </h1>
      <p className="text-base sm:text-lg text-muted mb-8 max-w-xl mx-auto">
        Найдите опытных репетиторов, бронируйте свободные слоты и подключайтесь к урокам через Zoom или Google Meet.
      </p>
      <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-stretch sm:items-center max-w-sm sm:max-w-none mx-auto">
        <Link to="/tutors" className="btn-primary w-full sm:w-auto">
          Смотреть репетиторов
        </Link>
        {!user && (
          <Link to="/register" className="btn-secondary w-full sm:w-auto">
            Начать
          </Link>
        )}
      </div>
    </div>
  );
}
