'use client';

import { useEffect, useState } from 'react';
import './Toast.css';

export type ToastType = 'success' | 'error' | 'info';

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastProps {
  toast: Toast;
  onRemove: (id: string) => void;
}

export default function ToastComponent({ toast, onRemove }: ToastProps) {
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsExiting(true);
      setTimeout(() => onRemove(toast.id), 300);
    }, 4000);

    return () => clearTimeout(timer);
  }, [toast.id, onRemove]);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => onRemove(toast.id), 300);
  };

  return (
    <div className={`toast toast-${toast.type} ${isExiting ? 'toast-exiting' : ''}`} role="alert">
      <div className="toast-content">
        <span className="toast-message">{toast.message}</span>
        <button className="toast-close" onClick={handleClose} aria-label="Close">
          ×
        </button>
      </div>
    </div>
  );
}

