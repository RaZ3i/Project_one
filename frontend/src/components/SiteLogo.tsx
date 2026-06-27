import { Link } from "react-router-dom";

export default function SiteLogo() {
  return (
    <Link
      to="/"
      className="inline-flex items-center gap-1.5 sm:gap-2 shrink-0 group"
      aria-label="TutorHub — на главную"
    >
      <img
        src="/favicon.svg"
        alt=""
        width={32}
        height={32}
        className="h-7 w-7 sm:h-8 sm:w-8 rounded-md"
        aria-hidden
      />
      <span className="text-base sm:text-lg md:text-xl font-semibold text-primary transition-colors group-hover:text-primary-600 dark:group-hover:text-primary-300">
        TutorHub
      </span>
    </Link>
  );
}
