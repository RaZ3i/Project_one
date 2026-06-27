export type ViewMode = "mobile" | "desktop";

const STORAGE_KEY = "site-view-mode";

export function getStoredViewMode(): ViewMode {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "mobile" || stored === "desktop") return stored;
  } catch {
    /* ignore */
  }
  return "mobile";
}

export function applyViewMode(mode: ViewMode) {
  const root = document.documentElement;
  root.classList.toggle("view-mode-desktop", mode === "desktop");
  root.classList.toggle("view-mode-mobile", mode === "mobile");
  root.dataset.viewMode = mode;
}

export function setStoredViewMode(mode: ViewMode) {
  try {
    localStorage.setItem(STORAGE_KEY, mode);
  } catch {
    /* ignore */
  }
  applyViewMode(mode);
}

export function initViewMode() {
  applyViewMode(getStoredViewMode());
}
