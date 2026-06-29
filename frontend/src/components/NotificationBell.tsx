import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch, type Notification, type NotificationType } from "../api/client";
import { formatDateTimeHHMM } from "../utils/formatDate";

// Bell icon: user-provided asset at /icons/bell.png

const TYPE_LABELS: Record<NotificationType, string> = {
  lesson_booked: "Новая запись",
  lesson_cancelled: "Отмена",
  lesson_completed: "Завершено",
  lesson_reminder: "Напоминание",
};

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  const { data: notifications } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => apiFetch<Notification[]>("/api/notifications/me"),
    refetchInterval: 30000,
  });

  const { data: unreadData } = useQuery({
    queryKey: ["notifications-unread"],
    queryFn: () => apiFetch<{ count: number }>("/api/notifications/me/unread-count"),
    refetchInterval: 30000,
  });

  const markRead = useMutation({
    mutationFn: (id: string) =>
      apiFetch<Notification>(`/api/notifications/${id}`, { method: "PATCH", body: JSON.stringify({ read: true }) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread"] });
    },
  });

  const markAllRead = useMutation({
    mutationFn: () => apiFetch("/api/notifications/mark-all-read", { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread"] });
    },
  });

  const unreadCount = unreadData?.count ?? 0;

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    if (open) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  return (
    <div className="relative" ref={panelRef}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="touch-target relative inline-flex items-center justify-center p-2 rounded-md hover:bg-secondary-100 dark:hover:bg-secondary-700 transition-colors"
        aria-label="Уведомления"
        title="Уведомления"
      >
        <img
          src="/icons/bell.png"
          alt=""
          className="w-5 h-5 dark:invert"
          width={20}
          height={20}
        />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 flex items-center justify-center rounded-full bg-red-500 text-white text-[10px] font-bold leading-none">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-80 max-w-[calc(100vw-2rem)] bg-surface border border-theme rounded-lg shadow-lg z-50 overflow-hidden">
          <div className="flex items-center justify-between px-3 py-2 border-b border-theme">
            <span className="font-medium text-sm">Уведомления</span>
            {unreadCount > 0 && (
              <button
                type="button"
                onClick={() => markAllRead.mutate()}
                className="text-xs text-primary hover:underline"
              >
                Прочитать все
              </button>
            )}
          </div>
          <div className="max-h-80 overflow-y-auto">
            {!notifications?.length ? (
              <p className="text-sm text-muted px-3 py-4 text-center">Нет уведомлений</p>
            ) : (
              notifications.map((n) => (
                <div
                  key={n.id}
                  className={`px-3 py-2.5 border-b border-theme last:border-0 ${
                    n.read ? "opacity-70" : "bg-primary-50/50 dark:bg-primary-900/20"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className="text-[10px] uppercase tracking-wide text-muted">
                          {TYPE_LABELS[n.type]}
                        </span>
                        {!n.read && <span className="w-1.5 h-1.5 rounded-full bg-primary-500 shrink-0" />}
                      </div>
                      <p className="text-sm font-medium leading-snug">{n.title}</p>
                      <p className="text-xs text-muted mt-0.5 leading-relaxed">{n.message}</p>
                      <p className="text-[10px] text-muted mt-1">{formatDateTimeHHMM(n.created_at)}</p>
                      {n.related_lesson_id && (
                        <Link
                          to={`/lessons/${n.related_lesson_id}`}
                          onClick={() => {
                            if (!n.read) markRead.mutate(n.id);
                            setOpen(false);
                          }}
                          className="text-xs text-primary hover:underline mt-1 inline-block"
                        >
                          Открыть занятие
                        </Link>
                      )}
                    </div>
                    {!n.read && (
                      <button
                        type="button"
                        onClick={() => markRead.mutate(n.id)}
                        className="text-[10px] text-primary hover:underline shrink-0"
                      >
                        ✓
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
