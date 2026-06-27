import { useEffect, useState } from "react";
import { getStoredTheme, getThemeToggleLabel, toggleTheme, type Theme } from "../hooks/useTheme";

export default function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(() => getStoredTheme());

  useEffect(() => {
    setTheme(getStoredTheme());
  }, []);

  const handleToggle = () => {
    setTheme(toggleTheme());
  };

  const label = getThemeToggleLabel(theme);

  return (
    <button
      type="button"
      onClick={handleToggle}
      className="touch-target inline-flex items-center justify-center rounded-md hover:bg-secondary-100 dark:hover:bg-secondary-700 transition-colors"
      aria-label={label}
      title={label}
    >
      <img
        src={theme === "dark" ? "/icons/sun.png" : "/icons/moon.png"}
        alt=""
        className="w-5 h-5"
        width={20}
        height={20}
      />
    </button>
  );
}
