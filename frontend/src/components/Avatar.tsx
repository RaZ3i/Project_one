// Icons style inspired by Flaticon - replace with licensed Flaticon assets if needed

const AVATAR_COLORS = [
  "bg-primary-400",
  "bg-primary-500",
  "bg-secondary-400",
  "bg-primary-300",
  "bg-secondary-500",
];

function initials(name: string): string {
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return name.slice(0, 2).toUpperCase();
}

function colorForName(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
}

type AvatarProps = {
  name: string;
  src?: string | null;
  size?: "sm" | "md" | "lg";
  className?: string;
};

const sizes = { sm: "w-10 h-10 text-sm", md: "w-16 h-16 text-lg", lg: "w-24 h-24 text-2xl" };

export default function Avatar({ name, src, size = "md", className = "" }: AvatarProps) {
  const API_BASE = import.meta.env.VITE_API_URL ?? "";
  const resolvedSrc = src?.startsWith("/") ? `${API_BASE}${src}` : src;

  if (resolvedSrc) {
    return (
      <img
        src={resolvedSrc}
        alt={name}
        className={`${sizes[size]} rounded-full object-cover border-2 border-theme ${className}`}
      />
    );
  }

  return (
    <div
      className={`${sizes[size]} ${colorForName(name)} rounded-full flex items-center justify-center text-white font-semibold border-2 border-theme ${className}`}
      aria-label={name}
    >
      {initials(name)}
    </div>
  );
}
