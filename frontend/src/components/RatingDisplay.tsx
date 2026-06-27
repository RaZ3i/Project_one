import { StarIcon } from "./icons";

export function StarRating({ rating, size = "sm" }: { rating: number; size?: "sm" | "md" }) {
  const cls = size === "md" ? "w-5 h-5" : "w-4 h-4";
  return (
    <span className="inline-flex items-center gap-0.5 text-amber-500">
      {[1, 2, 3, 4, 5].map((i) => (
        <StarIcon key={i} className={cls} filled={i <= Math.round(rating)} />
      ))}
    </span>
  );
}

export function RatingBadge({
  avgRating,
  reviewCount,
}: {
  avgRating: number | null;
  reviewCount: number;
}) {
  if (reviewCount === 0) {
    return <span className="text-sm text-muted">Нет отзывов</span>;
  }
  return (
    <span className="inline-flex items-center gap-1.5 text-sm">
      <StarRating rating={avgRating ?? 0} />
      <span className="font-medium">{avgRating?.toFixed(1)}</span>
      <span className="text-muted">({reviewCount})</span>
    </span>
  );
}
