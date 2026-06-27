export type Theme = "light" | "dark";

export const THEME_LABELS: Record<Theme, string> = {
  light: "Светлая тема",
  dark: "Тёмная тема",
};

export function getThemeLabel(theme: Theme): string {
  return THEME_LABELS[theme];
}

/** Label for the theme switch button (the theme you switch *to*). */
export function getThemeToggleLabel(current: Theme): string {
  return current === "dark" ? THEME_LABELS.light : THEME_LABELS.dark;
}

const STORAGE_KEY = "theme";

export function getStoredTheme(): Theme {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "dark" || stored === "light") return stored;
  return "light";
}

function enableThemeTransition(): void {
  document.documentElement.classList.add("theme-transition");
}

export function setStoredTheme(theme: Theme): void {
  localStorage.setItem(STORAGE_KEY, theme);
  enableThemeTransition();
  applyTheme(theme);
}

export function applyTheme(theme: Theme): void {
  const root = document.documentElement;
  if (theme === "dark") {
    root.classList.add("dark");
  } else {
    root.classList.remove("dark");
  }
}

export function initTheme(): void {
  applyTheme(getStoredTheme());
}

export function toggleTheme(): Theme {
  const next: Theme = getStoredTheme() === "dark" ? "light" : "dark";
  setStoredTheme(next);
  return next;
}
