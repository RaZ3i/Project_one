import { FormEvent, useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiUpload, type UserProfile, type UserGender } from "../api/client";
import { useAuth } from "../api/auth";
import Avatar from "./Avatar";
import { CameraIcon } from "./icons";

const GENDER_OPTIONS: { value: UserGender; label: string }[] = [
  { value: "male", label: "Мужской" },
  { value: "female", label: "Женский" },
];

const GENDER_LABELS: Record<UserGender, string> = {
  male: "Мужской",
  female: "Женский",
};

function ProfileField({ label, value }: { label: string; value: string | null | undefined }) {
  if (!value) return null;
  return (
    <div>
      <dt className="text-xs text-muted">{label}</dt>
      <dd className="text-sm">{value}</dd>
    </div>
  );
}

export default function ProfileCard() {
  const queryClient = useQueryClient();
  const { refreshUser } = useAuth();
  const fileRef = useRef<HTMLInputElement>(null);
  const [fullName, setFullName] = useState("");
  const [gender, setGender] = useState<UserGender | "">("");
  const [birthYear, setBirthYear] = useState("");
  const [phone, setPhone] = useState("");
  const [city, setCity] = useState("");
  const [saved, setSaved] = useState(false);
  const [editing, setEditing] = useState(false);

  const { data: profile, isLoading } = useQuery({
    queryKey: ["user-profile"],
    queryFn: () => apiFetch<UserProfile>("/api/users/me/profile"),
  });

  useEffect(() => {
    if (profile) {
      setFullName(profile.full_name);
      setGender(profile.gender ?? "");
      setBirthYear(profile.birth_year?.toString() ?? "");
      setPhone(profile.phone ?? "");
      setCity(profile.city ?? "");
    }
  }, [profile]);

  const refetchProfile = async (data?: UserProfile) => {
    if (data) {
      queryClient.setQueryData(["user-profile"], data);
    }
    await queryClient.refetchQueries({ queryKey: ["user-profile"] });
    await refreshUser();
  };

  const updateProfile = useMutation({
    mutationFn: () =>
      apiFetch<UserProfile>("/api/users/me/profile", {
        method: "PUT",
        body: JSON.stringify({
          full_name: fullName,
          gender: gender || null,
          birth_year: birthYear ? parseInt(birthYear, 10) : null,
          phone: phone || null,
          city: city || null,
        }),
      }),
    onSuccess: async (data) => {
      await refetchProfile(data);
      setSaved(true);
      setEditing(false);
      setTimeout(() => setSaved(false), 2000);
    },
  });

  const uploadAvatar = useMutation({
    mutationFn: (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return apiUpload<{ avatar_url: string }>("/api/users/me/avatar", form);
    },
    onSuccess: () => refetchProfile(),
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    updateProfile.mutate();
  };

  if (isLoading || !profile) return <p className="text-muted">Загрузка профиля...</p>;

  return (
    <div className="card-surface">
      <div className="flex flex-col sm:flex-row gap-4 items-start">
        <div className="relative shrink-0">
          <Avatar name={profile.full_name} src={profile.avatar_url} gender={profile.gender} size="lg" />
          <button
            type="button"
            onClick={() => fileRef.current?.click()}
            className="absolute bottom-0 right-0 touch-target bg-primary-500 text-white rounded-full p-1.5 hover:bg-primary-600"
            aria-label="Загрузить фото"
          >
            <CameraIcon className="w-4 h-4" />
          </button>
          <input
            ref={fileRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) uploadAvatar.mutate(file);
            }}
          />
        </div>
        <div className="flex-1 min-w-0">
          {!editing ? (
            <>
              <h2 className="text-lg font-semibold">{profile.full_name}</h2>
              <dl className="mt-2 space-y-2">
                <ProfileField label="Эл. почта" value={profile.email} />
                <ProfileField label="Пол" value={profile.gender ? GENDER_LABELS[profile.gender] : null} />
                <ProfileField label="Год рождения" value={profile.birth_year?.toString()} />
                <ProfileField label="Телефон" value={profile.phone} />
                <ProfileField label="Город" value={profile.city} />
              </dl>
              <button type="button" onClick={() => setEditing(true)} className="text-primary text-sm mt-3 hover:underline">
                Редактировать профиль
              </button>
            </>
          ) : (
            <p className="text-sm text-muted">Редактирование профиля</p>
          )}
        </div>
      </div>

      {editing && (
        <form onSubmit={handleSubmit} className="mt-4 space-y-3 border-t border-theme pt-4">
          <div>
            <label className="block text-sm font-medium mb-1">Имя</label>
            <input value={fullName} onChange={(e) => setFullName(e.target.value)} className="form-input" required />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">Пол</label>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value as UserGender | "")}
                className="form-input"
              >
                <option value="">Не указан</option>
                {GENDER_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Год рождения</label>
              <input
                type="number"
                min={1900}
                max={2100}
                value={birthYear}
                onChange={(e) => setBirthYear(e.target.value)}
                className="form-input"
                placeholder="2008"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">Телефон</label>
              <input value={phone} onChange={(e) => setPhone(e.target.value)} className="form-input" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Город</label>
              <input value={city} onChange={(e) => setCity(e.target.value)} className="form-input" />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" disabled={updateProfile.isPending} className="btn-primary text-sm">
              Сохранить
            </button>
            <button type="button" onClick={() => setEditing(false)} className="btn-secondary text-sm">
              Отмена
            </button>
          </div>
        </form>
      )}
      {saved && <p className="text-green-600 dark:text-green-400 text-sm mt-2">Сохранено!</p>}
    </div>
  );
}
