import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useEffect, useState } from "react";
import { ApiError, apiFetch, type Lesson, type Slot, type TutorDetail } from "../api/client";
import { useAuth } from "../api/auth";

function formatDate(iso: string) {
  return new Date(iso).toLocaleString();
}

export default function TutorDashboard() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [startsAt, setStartsAt] = useState("");
  const [endsAt, setEndsAt] = useState("");
  const [slotError, setSlotError] = useState("");
  const [profileBio, setProfileBio] = useState("");
  const [profileSubjects, setProfileSubjects] = useState("");
  const [profileMeetingUrl, setProfileMeetingUrl] = useState("");
  const [profileSaved, setProfileSaved] = useState(false);

  const { data: profile } = useQuery({
    queryKey: ["my-profile"],
    queryFn: () => apiFetch<TutorDetail>(`/api/tutors/${user!.id}`),
    enabled: !!user,
  });

  useEffect(() => {
    if (profile) {
      setProfileBio(profile.bio ?? "");
      setProfileSubjects(profile.subjects ?? "");
      setProfileMeetingUrl(profile.default_meeting_url ?? "");
    }
  }, [profile]);

  const { data: slots } = useQuery({
    queryKey: ["my-slots"],
    queryFn: () => apiFetch<Slot[]>(`/api/slots?tutor_id=${user!.id}&available_only=false`),
    enabled: !!user,
  });

  const { data: lessons } = useQuery({
    queryKey: ["my-lessons"],
    queryFn: () => apiFetch<Lesson[]>("/api/lessons/me"),
  });

  const createSlot = useMutation({
    mutationFn: () =>
      apiFetch("/api/slots", {
        method: "POST",
        body: JSON.stringify({ starts_at: new Date(startsAt).toISOString(), ends_at: new Date(endsAt).toISOString() }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-slots"] });
      setStartsAt("");
      setEndsAt("");
      setSlotError("");
    },
    onError: (err) => setSlotError(err instanceof ApiError ? err.message : "Failed to create slot"),
  });

  const deleteSlot = useMutation({
    mutationFn: (id: string) => apiFetch(`/api/slots/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["my-slots"] }),
  });

  const updateProfile = useMutation({
    mutationFn: () =>
      apiFetch(`/api/tutors/me/profile`, {
        method: "PUT",
        body: JSON.stringify({
          bio: profileBio,
          subjects: profileSubjects,
          default_meeting_url: profileMeetingUrl || null,
        }),
      }),
    onSuccess: () => {
      setProfileSaved(true);
      setTimeout(() => setProfileSaved(false), 2000);
    },
  });

  const handleCreateSlot = (e: FormEvent) => {
    e.preventDefault();
    if (!startsAt || !endsAt) return;
    createSlot.mutate();
  };

  return (
    <div className="space-y-10">
      <section>
        <h1 className="text-2xl font-bold mb-6">Tutor Dashboard</h1>
        <h2 className="text-lg font-semibold mb-3">My Profile</h2>
        <form onSubmit={(e) => { e.preventDefault(); updateProfile.mutate(); }} className="bg-white p-4 rounded-lg border space-y-3 max-w-lg">
          <div>
            <label className="block text-sm font-medium mb-1">Subjects</label>
            <input value={profileSubjects} onChange={(e) => setProfileSubjects(e.target.value)} className="w-full border rounded-md px-3 py-2" placeholder="Math, Physics" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Bio</label>
            <textarea value={profileBio} onChange={(e) => setProfileBio(e.target.value)} className="w-full border rounded-md px-3 py-2" rows={3} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Default meeting URL</label>
            <input value={profileMeetingUrl} onChange={(e) => setProfileMeetingUrl(e.target.value)} className="w-full border rounded-md px-3 py-2" placeholder="https://zoom.us/j/..." />
          </div>
          <button type="submit" className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm hover:bg-indigo-700">
            Save Profile
          </button>
          {profileSaved && <span className="text-green-600 text-sm ml-2">Saved!</span>}
        </form>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3">Availability Slots</h2>
        <form onSubmit={handleCreateSlot} className="bg-white p-4 rounded-lg border space-y-3 max-w-lg mb-4">
          {slotError && <p className="text-red-600 text-sm">{slotError}</p>}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">Starts at</label>
              <input type="datetime-local" required value={startsAt} onChange={(e) => setStartsAt(e.target.value)} className="w-full border rounded-md px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Ends at</label>
              <input type="datetime-local" required value={endsAt} onChange={(e) => setEndsAt(e.target.value)} className="w-full border rounded-md px-3 py-2" />
            </div>
          </div>
          <button type="submit" disabled={createSlot.isPending} className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm hover:bg-indigo-700 disabled:opacity-50">
            Add Slot
          </button>
        </form>
        <div className="space-y-2">
          {slots?.map((slot) => (
            <div key={slot.id} className="flex justify-between items-center bg-white p-3 rounded-lg border">
              <span className="text-sm">
                {formatDate(slot.starts_at)} – {formatDate(slot.ends_at)}
                {slot.is_booked && <span className="ml-2 text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded">booked</span>}
              </span>
              {!slot.is_booked && (
                <button onClick={() => deleteSlot.mutate(slot.id)} className="text-red-600 text-sm hover:underline">Delete</button>
              )}
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3">My Lessons</h2>
        <div className="space-y-3">
          {lessons?.map((lesson) => (
            <TutorLessonCard key={lesson.id} lesson={lesson} />
          ))}
          {lessons?.length === 0 && <p className="text-slate-500">No lessons yet.</p>}
        </div>
      </section>
    </div>
  );
}

function TutorLessonCard({ lesson }: { lesson: Lesson }) {
  const queryClient = useQueryClient();
  const [meetingUrl, setMeetingUrl] = useState(lesson.meeting_url ?? "");

  const updateLesson = useMutation({
    mutationFn: (body: Record<string, string>) =>
      apiFetch(`/api/lessons/${lesson.id}`, { method: "PATCH", body: JSON.stringify(body) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["my-lessons"] }),
  });

  return (
    <div className="bg-white p-4 rounded-lg border">
      <p className="font-medium">{lesson.student_name}</p>
      <p className="text-sm text-slate-500">{formatDate(lesson.slot_starts_at ?? lesson.created_at)}</p>
      <span className="inline-block mt-1 text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700">{lesson.status}</span>
      {lesson.status === "scheduled" && (
        <div className="mt-3 flex gap-2 items-center flex-wrap">
          <input
            value={meetingUrl}
            onChange={(e) => setMeetingUrl(e.target.value)}
            placeholder="Meeting URL for this lesson"
            className="border rounded-md px-3 py-1.5 text-sm flex-1 min-w-[200px]"
          />
          <button
            onClick={() => updateLesson.mutate({ meeting_url: meetingUrl })}
            className="text-indigo-600 text-sm hover:underline"
          >
            Save URL
          </button>
          <button
            onClick={() => updateLesson.mutate({ status: "completed" })}
            className="bg-green-600 text-white px-3 py-1 rounded text-sm"
          >
            Complete
          </button>
        </div>
      )}
    </div>
  );
}
