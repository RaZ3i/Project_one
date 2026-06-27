import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../api/auth";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState<"student" | "tutor">("student");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register({ email, password, full_name: fullName, role });
      navigate(role === "tutor" ? "/tutor/dashboard" : "/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось зарегистрироваться");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto w-full">
      <h1 className="page-title">Создать аккаунт</h1>
      <form onSubmit={handleSubmit} className="space-y-4 card-surface">
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <div>
          <label className="block text-sm font-medium mb-1">Полное имя</label>
          <input
            type="text"
            required
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="form-input"
            autoComplete="name"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Эл. почта</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="form-input"
            autoComplete="email"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Пароль (мин. 8 символов)</label>
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="form-input"
            autoComplete="new-password"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Я —</label>
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
            <label className="flex items-center gap-2 touch-target cursor-pointer">
              <input
                type="radio"
                name="role"
                checked={role === "student"}
                onChange={() => setRole("student")}
              />
              Ученик
            </label>
            <label className="flex items-center gap-2 touch-target cursor-pointer">
              <input
                type="radio"
                name="role"
                checked={role === "tutor"}
                onChange={() => setRole("tutor")}
              />
              Репетитор
            </label>
          </div>
        </div>
        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? "Создание..." : "Зарегистрироваться"}
        </button>
      </form>
      <p className="text-center mt-4 text-sm text-muted">
        Уже есть аккаунт?{" "}
        <Link to="/login" className="text-primary hover:underline touch-target inline-flex items-center">
          Войти
        </Link>
      </p>
    </div>
  );
}
