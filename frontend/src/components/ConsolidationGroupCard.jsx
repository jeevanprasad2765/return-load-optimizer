import React from 'react';
import { Layers, CheckCircle, Package, ArrowRight, Weight, DollarSign } from 'lucide-react';

export const ConsolidationGroupCard = ({ group, onAcceptGroup }) => {
  const {
    group_id, shipments, matches, total_weight_kg, total_capacity_kg,
    capacity_utilization_pct, combined_score, total_estimated_revenue
  } = group;

  return (
    <div className="glass-panel rounded-2xl p-6 border-purple-500/30 bg-purple-950/20 relative overflow-hidden transition-all hover:border-purple-500/50 mb-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-purple-900/40 pb-4 mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-purple-600 text-white shadow-md shadow-purple-600/20">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              Consolidated Match Group ({shipments.length} Shipments)
            </h4>
            <p className="text-xs text-purple-300">
              Multiple small shipments combined into a single return load
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <span className="px-3 py-1.5 rounded-xl bg-purple-500/20 text-purple-300 font-extrabold text-sm border border-purple-500/30">
            {capacity_utilization_pct}% Load Fill
          </span>
          <div className="px-4 py-1.5 rounded-xl bg-emerald-500/20 text-emerald-300 font-extrabold text-lg border border-emerald-500/30">
            {combined_score}/100
          </div>
        </div>
      </div>

      {/* Shipments Included List */}
      <div className="space-y-2 mb-4">
        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
          Included Freight Loads:
        </div>
        {shipments.map((s, idx) => (
          <div key={s.id || idx} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/80 flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2">
              <Package className="w-4 h-4 text-amber-400 flex-shrink-0" />
              <span className="font-bold text-slate-100">{s.goods_type}</span>
              <span className="text-slate-400">({s.pickup_name} <ArrowRight className="w-3 h-3 inline text-slate-500" /> {s.dest_name})</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="font-semibold text-purple-300">{s.weight_kg} kg</span>
              <span className="font-bold text-emerald-400">₹{matches[idx]?.estimated_revenue?.toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Aggregate Metrics & Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-purple-900/40">
        <div className="text-xs text-slate-300 space-y-1">
          <div>Total Consolidated Weight: <strong className="text-white">{total_weight_kg} kg</strong> / {total_capacity_kg} kg</div>
          <div>Total Estimated Earnings: <strong className="text-emerald-400 text-sm">₹{total_estimated_revenue?.toLocaleString()}</strong></div>
        </div>

        {onAcceptGroup && (
          <button
            onClick={() => onAcceptGroup(group)}
            className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs transition-all shadow-lg shadow-purple-600/25 flex items-center gap-1.5"
          >
            <CheckCircle className="w-4 h-4" /> Accept Consolidated Load Group
          </button>
        )}
      </div>
    </div>
  );
};
