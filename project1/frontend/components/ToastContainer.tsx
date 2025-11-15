'use client';

import { useState, useCallback } from 'react';
import Toast, { type Toast as ToastType } from './Toast';
import './ToastContainer.css';

export const useToast = () => {
  const [toasts, setToasts] = useState<ToastType[]>([]);

  const showToast = useCallback((message: string, type: ToastType['type'] = 'info') => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast: ToastType = { id, message, type };
    setToasts((prev) => [...prev, newToast]);
    return id;
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  return { toasts, showToast, removeToast };
};

export default function ToastContainer({ toasts, onRemove }: { toasts: ToastType[]; onRemove: (id: string) => void }) {
  return (
    <div className="toast-container" aria-live="polite" aria-atomic="true">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onRemove={onRemove} />
      ))}
    </div>
  );
}

