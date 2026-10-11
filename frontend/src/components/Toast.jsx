import React, { useEffect } from 'react';
import { CheckCircle, AlertCircle, X } from 'lucide-react';

export const Toast = ({ message, type = 'success', onClose, duration = 4000 }) => {
  useEffect(() => {
    if (!message || !onClose) return;
    const timer = setTimeout(() => {
      onClose();
    }, duration);
    return () => clearTimeout(timer);
  }, [message, onClose, duration]);

  if (!message) return null;

  const isSuccess = type === 'success';

  return (
    <div className="fixed bottom-6 right-6 z-50 transition-all duration-300">
      <div
        className={`flex items-center gap-3 px-4 py-3 rounded-2xl shadow-2xl border backdrop-blur-md ${
          isSuccess
            ? 'bg-slate-900/95 text-emerald-200 border-emerald-500/40 shadow-emerald-950/50'
            : 'bg-slate-900/95 text-rose-200 border-rose-500/40 shadow-rose-950/50'
        }`}
      >
        {isSuccess ? (
          <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
        ) : (
          <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
        )}
        <span className="text-xs font-semibold">{message}</span>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-colors ml-2"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </div>
  );
};
