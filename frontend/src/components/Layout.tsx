import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuth } from "../api/auth";
import ViewModeToggle from "./ViewModeToggle";
import ThemeToggle from "./ThemeToggle";

function NavLink({
  to,
  children,
  className = "",
  onClick,
}: {
  to: string;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}) {
  const location = useLocation();
  const active = location.pathname === to || (to !== "/" && location.pathname.startsWith(to));

  return (
    <Link
      to={to}
      onClick={onClick}
      className={`touch-target inline-flex items-center px-3 py-2 rounded-md transition-colors ${
        active
          ? "text-primary font-medium bg-primary-50 dark:bg-primary-900/30"
          : "text-secondary-700 dark:text-secondary-300 hover:text-primary"
      } ${className}`}
    >
      {children}
    </Link>
  );
}

function BottomNavItem({ to, label }: { to: string; label: string }) {
  const location = useLocation();
  const active =
    location.pathname === to || (to !== "/" && location.pathname.startsWith(to));

  return (
    <Link
      to={to}
      className={`flex flex-col items-center justify-center gap-0.5 flex-1 min-h-[44px] py-2 text-xs transition-colors ${
        active ? "text-primary font-medium" : "text-muted hover:text-primary"
      }`}
    >
      <span
        className={`w-5 h-5 rounded ${active ? "bg-primary-500" : "bg-secondary-300 dark:bg-secondary-600"}`}
        aria-hidden
      />
      {label}
    </Link>
  );
}

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  const dashboardPath = user?.role === "tutor" ? "/tutor/dashboard" : "/dashboard";

  const handleLogout = () => {
    logout();
    setMenuOpen(false);
    navigate("/login");
  };

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex flex-col pb-safe-bottom md:pb-0">
      <header className="bg-surface border-b border-theme sticky top-0 z-40 pt-safe-top">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3 md:py-4 flex items-center justify-between gap-3">
          <Link to="/" className="text-lg sm:text-xl font-semibold text-primary shrink-0">
            TutorHub
          </Link>

          <nav className="hidden md:flex items-center gap-1 lg:gap-2 text-sm">
            <NavLink to="/tutors">Репетиторы</NavLink>
            {user ? (
              <>
                <NavLink to={dashboardPath}>Личный кабинет</NavLink>
                <span className="text-muted px-2 hidden lg:inline">{user.full_name}</span>
                <button
                  onClick={handleLogout}
                  className="touch-target text-red-600 dark:text-red-400 hover:underline px-3 py-2"
                >
                  Выйти
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login">Войти</NavLink>
                <Link
                  to="/register"
                  className="touch-target bg-primary-500 text-white px-4 py-2 rounded-md hover:bg-primary-600 ml-1"
                >
                  Регистрация
                </Link>
              </>
            )}
            <ThemeToggle />
            <ViewModeToggle />
          </nav>

          <div className="flex items-center gap-1 md:hidden">
            <ThemeToggle />
            <ViewModeToggle />
            <button
              type="button"
              onClick={() => setMenuOpen((o) => !o)}
              className="touch-target p-2 -mr-2 rounded-md hover:bg-secondary-100 dark:hover:bg-secondary-700"
              aria-expanded={menuOpen}
              aria-label={menuOpen ? "Закрыть меню" : "Открыть меню"}
            >
              <span className="sr-only">{menuOpen ? "Закрыть" : "Меню"}</span>
              <div className="w-6 h-5 flex flex-col justify-between" aria-hidden>
                <span className={`block h-0.5 bg-secondary-700 dark:bg-secondary-300 transition-transform ${menuOpen ? "translate-y-2 rotate-45" : ""}`} />
                <span className={`block h-0.5 bg-secondary-700 dark:bg-secondary-300 transition-opacity ${menuOpen ? "opacity-0" : ""}`} />
                <span className={`block h-0.5 bg-secondary-700 dark:bg-secondary-300 transition-transform ${menuOpen ? "-translate-y-2 -rotate-45" : ""}`} />
              </div>
            </button>
          </div>
        </div>

        {menuOpen && (
          <nav className="md:hidden border-t border-theme bg-surface px-4 py-3 space-y-1">
            <NavLink to="/tutors" onClick={() => setMenuOpen(false)} className="block w-full">
              Репетиторы
            </NavLink>
            {user ? (
              <>
                <NavLink to={dashboardPath} onClick={() => setMenuOpen(false)} className="block w-full">
                  Личный кабинет
                </NavLink>
                <p className="px-3 py-2 text-sm text-muted">{user.full_name}</p>
                <button
                  onClick={handleLogout}
                  className="touch-target block w-full text-left text-red-600 dark:text-red-400 px-3 py-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md"
                >
                  Выйти
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login" onClick={() => setMenuOpen(false)} className="block w-full">
                  Войти
                </NavLink>
                <Link
                  to="/register"
                  onClick={() => setMenuOpen(false)}
                  className="touch-target block w-full bg-primary-500 text-white px-3 py-2.5 rounded-md text-center hover:bg-primary-600 mt-2"
                >
                  Регистрация
                </Link>
              </>
            )}
          </nav>
        )}
      </header>

      <main className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 py-6 sm:py-8 pb-bottom-nav md:pb-8">
        <Outlet />
      </main>

      <footer className="hidden md:block border-t border-theme bg-surface py-4">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 flex items-center justify-between text-sm text-muted">
          <span>TutorHub — платформа репетиторства</span>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <ViewModeToggle />
          </div>
        </div>
      </footer>

      <nav className="md:hidden fixed bottom-0 inset-x-0 z-40 bg-surface border-t border-theme pb-safe-bottom flex">
        <BottomNavItem to="/" label="Главная" />
        <BottomNavItem to="/tutors" label="Репетиторы" />
        <BottomNavItem
          to={user ? dashboardPath : "/login"}
          label={user ? "Кабинет" : "Войти"}
        />
        <BottomNavItem to={user ? dashboardPath : "/register"} label={user ? "Профиль" : "Регистр."} />
      </nav>
    </div>
  );
}
