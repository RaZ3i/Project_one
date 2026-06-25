import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { useAuth } from "./api/auth";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import StudentDashboard from "./pages/StudentDashboard";
import TutorDashboard from "./pages/TutorDashboard";
import TutorDetailPage from "./pages/TutorDetailPage";
import TutorsPage from "./pages/TutorsPage";

function DashboardRedirect() {
  const { user, loading } = useAuth();
  if (loading) return <div className="text-center py-12">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={user.role === "tutor" ? "/tutor/dashboard" : "/dashboard"} replace />;
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="tutors" element={<TutorsPage />} />
        <Route path="tutors/:id" element={<TutorDetailPage />} />
        <Route path="dashboard" element={<ProtectedRoute role="student" />}>
          <Route index element={<StudentDashboard />} />
        </Route>
        <Route path="tutor/dashboard" element={<ProtectedRoute role="tutor" />}>
          <Route index element={<TutorDashboard />} />
        </Route>
        <Route path="dashboard-redirect" element={<DashboardRedirect />} />
      </Route>
    </Routes>
  );
}
