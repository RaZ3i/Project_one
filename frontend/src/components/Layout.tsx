import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../api/auth";

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/" className="text-xl font-semibold text-indigo-600">
            TutorHub
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            <Link to="/tutors" className="hover:text-indigo-600">
              Tutors
            </Link>
            {user ? (
              <>
                <Link
                  to={user.role === "tutor" ? "/tutor/dashboard" : "/dashboard"}
                  className="hover:text-indigo-600"
                >
                  Dashboard
                </Link>
                <span className="text-slate-500">{user.full_name}</span>
                <button onClick={handleLogout} className="text-red-600 hover:underline">
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="hover:text-indigo-600">
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-indigo-600 text-white px-3 py-1.5 rounded-md hover:bg-indigo-700"
                >
                  Register
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="max-w-5xl mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
