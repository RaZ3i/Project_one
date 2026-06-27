import { useEffect, useState } from "react";
import {
  getStoredViewMode,
  setStoredViewMode,
  type ViewMode,
} from "../hooks/useViewMode";

export default function ViewModeToggle() {
  const [mode, setMode] = useState<ViewMode>(() => getStoredViewMode());

  useEffect(() => {
    setMode(getStoredViewMode());
  }, []);

  const toggle = () => {
    const next: ViewMode = mode === "mobile" ? "desktop" : "mobile";
    setStoredViewMode(next);
    setMode(next);
  };

  return (
    <button
      type="button"
      onClick={toggle}
      className="view-mode-toggle touch-target text-sm text-muted hover:text-primary transition-colors"
      aria-label={mode === "mobile" ? "Переключить на полную версию" : "Переключить на мобильную версию"}
    >
      {mode === "mobile" ? "Полная версия" : "Мобильная версия"}
    </button>
  );
}
