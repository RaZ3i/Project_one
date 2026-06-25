const API_BASE = import.meta.env.VITE_API_URL ?? "";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number
  ) {
    super(message);
  }
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem("token");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
      if (Array.isArray(detail)) {
        detail = detail.map((d: { msg?: string }) => d.msg ?? JSON.stringify(d)).join(", ");
      }
    } catch {
      /* игнорировать */
    }
    throw new ApiError(String(detail), res.status);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return res.json();
}

export type UserRole = "student" | "tutor";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface TutorListItem {
  id: string;
  full_name: string;
  subjects: string | null;
  bio: string | null;
}

export interface TutorDetail {
  id: string;
  full_name: string;
  email: string;
  subjects: string | null;
  bio: string | null;
  default_meeting_url: string | null;
}

export interface Slot {
  id: string;
  tutor_id: string;
  starts_at: string;
  ends_at: string;
  is_booked: boolean;
}

export type LessonStatus = "scheduled" | "completed" | "cancelled";

export const LESSON_STATUS_LABELS: Record<LessonStatus, string> = {
  scheduled: "Запланировано",
  completed: "Завершено",
  cancelled: "Отменено",
};

export interface Lesson {
  id: string;
  student_id: string;
  tutor_id: string;
  slot_id: string;
  status: LessonStatus;
  meeting_url: string | null;
  effective_meeting_url: string | null;
  notes: string | null;
  created_at: string;
  slot_starts_at: string | null;
  slot_ends_at: string | null;
  student_name: string | null;
  tutor_name: string | null;
}
