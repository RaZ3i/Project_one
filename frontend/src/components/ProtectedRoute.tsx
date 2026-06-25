import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../api/auth";

export function ProtectedRoute({ role }: { role?: "student" | "tutor" }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="text-center py-12 text-slate-500">Загрузка...</div>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (role && user.role !== role) {
    return <Navigate to={user.role === "tutor" ? "/tutor/dashboard" : "/dashboard"} replace />;
  }
  return <Outlet />;
}
