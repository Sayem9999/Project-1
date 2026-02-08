'use client';
import { createContext, useContext, useState, useCallback, ReactNode } from 'react';

type ToastType = 'success' | 'error' | 'info';

interface Toast {
    id: number;
    message: string;
    type: ToastType;
}

interface ToastContextType {
    showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
    const context = useContext(ToastContext);
    if (!context) throw new Error('useToast must be used within ToastProvider');
    return context;
}

export function ToastProvider({ children }: { children: ReactNode }) {
    const [toasts, setToasts] = useState<Toast[]>([]);

    const showToast = useCallback((message: string, type: ToastType = 'info') => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, message, type }]);
        setTimeout(() => {
            setToasts(prev => prev.filter(t => t.id !== id));
        }, 4000);
    }, []);

    const getToastStyles = (type: ToastType) => {
        switch (type) {
            case 'success': return 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300';
            case 'error': return 'bg-red-500/20 border-red-500/50 text-red-300';
            default: return 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300';
        }
    };

    const getIcon = (type: ToastType) => {
        switch (type) {
            case 'success': return '✓';
            case 'error': return '✕';
            default: return 'ℹ';
        }
    };

    return (
        <ToastContext.Provider value={{ showToast }}>
            {children}

            {/* Toast Container */}
            <div className="fixed bottom-4 right-4 z-50 space-y-2">
                {toasts.map(toast => (
                    <div
                        key={toast.id}
                        className={`flex items-center gap-3 px-4 py-3 rounded-xl border backdrop-blur-md ${getToastStyles(toast.type)}`}
                        style={{ animation: 'slideUp 0.3s ease-out' }}
                    >
                        <span className="text-lg">{getIcon(toast.type)}</span>
                        <p className="text-sm font-medium">{toast.message}</p>
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
}
