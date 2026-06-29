import { FormEvent, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { ApiError, apiFetch } from "../api/client";

interface CancelLessonModalProps {
  lessonId: string;
  onClose: () => void;
  onSuccess: () => void;
}

export default function CancelLessonModal({ lessonId, onClose, onSuccess }: CancelLessonModalProps) {
  const [reason, setReason] = useState("");
  const [error, setError] = useState("");

  const cancelMutation = useMutation({
    mutationFn: () =>
      apiFetch(`/api/lessons/${lessonId}`, {
        method: "PATCH",
        body: JSON.stringify({ status: "cancelled", cancellation_reason: reason.trim() }),
      }),
    onSuccess: () => {
      onSuccess();
      onClose();
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Не удалось отменить занятие"),
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!reason.trim()) {
      setError("Укажите причину отмены");
      return;
    }
    cancelMutation.mutate();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={onClose}>
      <div
        className="card-surface w-full max-w-md space-y-4"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="cancel-modal-title"
      >
        <h3 id="cancel-modal-title" className="font-semibold text-lg">
          Отменить занятие
        </h3>
        <p className="text-sm text-muted">Укажите причину отмены — ученик получит уведомление.</p>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-3">
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="form-input min-h-[88px] py-2 text-sm"
            placeholder="Причина отмены..."
            required
            autoFocus
          />
          <div className="flex gap-2 justify-end">
            <button type="button" onClick={onClose} className="btn-secondary text-sm">
              Назад
            </button>
            <button type="submit" disabled={cancelMutation.isPending} className="btn-danger-text text-sm px-4 py-2 border border-red-600 rounded">
              Отменить занятие
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
