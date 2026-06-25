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
      setError(err instanceof ApiError ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-6">Create account</h1>
      <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow-sm border">
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <div>
          <label className="block text-sm font-medium mb-1">Full name</label>
          <input
            type="text"
            required
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="w-full border rounded-md px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border rounded-md px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Password (min 8 chars)</label>
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border rounded-md px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">I am a</label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="role"
                checked={role === "student"}
                onChange={() => setRole("student")}
              />
              Student
            </label>
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="role"
                checked={role === "tutor"}
                onChange={() => setRole("tutor")}
              />
              Tutor
            </label>
          </div>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? "Creating..." : "Register"}
        </button>
      </form>
      <p className="text-center mt-4 text-sm text-slate-600">
        Already have an account?{" "}
        <Link to="/login" className="text-indigo-600 hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
