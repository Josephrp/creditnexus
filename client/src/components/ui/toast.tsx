import { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import { X, CheckCircle2, AlertCircle, Info, AlertTriangle } from 'lucide-react';

type ToastType = 'success' | 'error' | 'info' | 'warning';

interface Toast {
  id: string;
  message?: string;
  title?: string;
  description?: string;
  type: ToastType;
  duration?: number;
}

type ToastOptions = {
  title?: string;
  description?: string;
  message?: string;
  type?: ToastType;
  duration?: number;
};

interface ToastContextType {
  toasts: Toast[];
  addToast: {
    (message: string, type?: ToastType, duration?: number): void;
    (options: ToastOptions): void;
  };
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

const toastIcons = {
  success: <CheckCircle2 className="h-5 w-5 text-emerald-400" />,
  error: <AlertCircle className="h-5 w-5 text-red-400" />,
  info: <Info className="h-5 w-5 text-blue-400" />,
  warning: <AlertTriangle className="h-5 w-5 text-yellow-400" />,
};

const toastStyles = {
  success: 'border-emerald-500/30 bg-emerald-500/10',
  error: 'border-red-500/30 bg-red-500/10',
  info: 'border-blue-500/30 bg-blue-500/10',
  warning: 'border-yellow-500/30 bg-yellow-500/10',
};

function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: () => void }) {
  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-lg border backdrop-blur-sm shadow-lg animate-slide-in ${toastStyles[toast.type]}`}
      role="alert"
    >
      {toastIcons[toast.type]}
      <div className="flex-1">
        {toast.title && <p className="text-sm font-semibold text-slate-100">{toast.title}</p>}
        {toast.description && <p className="text-sm text-slate-300">{toast.description}</p>}
        {!toast.title && !toast.description && (
          <p className="text-sm text-slate-100">{toast.message}</p>
        )}
      </div>
      <button
        onClick={onRemove}
        className="text-slate-400 hover:text-white transition-colors"
        aria-label="Dismiss"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback(
    (arg1: string | ToastOptions, arg2: ToastType = 'info', arg3 = 5000) => {
      const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      let toast: Toast;

      if (typeof arg1 === 'string') {
        toast = {
          id,
          message: arg1,
          type: arg2,
          duration: arg3,
        };
      } else {
        toast = {
          id,
          title: arg1.title,
          description: arg1.description ?? arg1.message,
          message: arg1.message,
          type: arg1.type ?? 'info',
          duration: arg1.duration ?? 5000,
        };
      }

      setToasts(prev => [...prev, toast]);

      if ((toast.duration ?? 0) > 0) {
        setTimeout(() => {
          setToasts(prev => prev.filter(t => t.id !== id));
        }, toast.duration);
      }
    },
    []
  );

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
        {toasts.map(toast => (
          <ToastItem
            key={toast.id}
            toast={toast}
            onRemove={() => removeToast(toast.id)}
          />
        ))}
      </div>
    </ToastContext.Provider>
  );
}
