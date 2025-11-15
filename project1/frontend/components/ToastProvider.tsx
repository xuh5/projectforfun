'use client';

import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import ToastContainer, { useToast as useToastHook } from './ToastContainer';
import type { Toast } from './Toast';

interface ToastContextType {
  showToast: (message: string, type?: Toast['type']) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const { toasts, showToast: showToastHook, removeToast } = useToastHook();

  const showToast = useCallback((message: string, type: Toast['type'] = 'info') => {
    showToastHook(message, type);
  }, [showToastHook]);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
}

