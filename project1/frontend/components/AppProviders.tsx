'use client';

import { ErrorBoundary } from './ErrorBoundary';
import { ToastProvider } from './ToastProvider';

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary>
      <ToastProvider>{children}</ToastProvider>
    </ErrorBoundary>
  );
}

