import React from 'react';

export const StatusBadge = ({ status }) => {
  const normalized = (status || '').toLowerCase();

  const styles = {
    posted: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    booking_requested: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
    pending: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
    matched: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    accepted: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    confirmed: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    booked: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    in_transit: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/20',
    delivered: 'bg-teal-500/10 text-teal-300 border-teal-500/20',
    rejected: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    cancelled: 'bg-slate-800 text-slate-400 border-slate-700',
  };

  const style = styles[normalized] || 'bg-slate-800 text-slate-300 border-slate-700';
  const label = (status || '').replace(/_/g, ' ');

  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border uppercase tracking-wider ${style}`}>
      {label}
    </span>
  );
};
