import { Link } from "react-router-dom";
import { useAuth } from "../api/auth";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <div className="text-center py-16">
      <h1 className="text-4xl font-bold text-slate-900 mb-4">1-on-1 Tutoring Platform</h1>
      <p className="text-lg text-slate-600 mb-8 max-w-xl mx-auto">
        Find expert tutors, book available time slots, and join lessons via Zoom or Google Meet.
      </p>
      <div className="flex gap-4 justify-center">
        <Link
          to="/tutors"
          className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700"
        >
          Browse Tutors
        </Link>
        {!user && (
          <Link
            to="/register"
            className="border border-indigo-600 text-indigo-600 px-6 py-3 rounded-lg font-medium hover:bg-indigo-50"
          >
            Get Started
          </Link>
        )}
      </div>
    </div>
  );
}
