import React from 'react';
import { Route, DollarSign, TrendingUp, Truck, Leaf } from 'lucide-react';

export const MetricsCards = ({ metrics }) => {
  if (!metrics) return null;

  const items = [
    {
      title: 'Empty Km Reduced',
      value: `${(metrics.empty_km_reduced ?? 0).toLocaleString()} km`,
      subtext: 'Return distance filled',
      icon: Route,
      color: 'from-blue-500 to-indigo-600',
      textColor: 'text-blue-400',
    },
    {
      title: 'Additional Revenue',
      value: `₹${(metrics.additional_revenue_generated ?? 0).toLocaleString()}`,
      subtext: 'Earned by carriers',
      icon: DollarSign,
      color: 'from-emerald-500 to-teal-600',
      textColor: 'text-emerald-400',
    },
    {
      title: 'Cost Saved',
      value: `₹${(metrics.cost_saved_for_shippers ?? 0).toLocaleString()}`,
      subtext: 'Saved by shippers',
      icon: TrendingUp,
      color: 'from-amber-500 to-orange-600',
      textColor: 'text-amber-400',
    },
    {
      title: 'Vehicle Utilization',
      value: `${metrics.average_vehicle_utilization_pct ?? 0}%`,
      subtext: 'Average capacity filled',
      icon: Truck,
      color: 'from-purple-500 to-pink-600',
      textColor: 'text-purple-400',
    },
    {
      title: 'CO₂ Emissions Saved',
      value: `${(metrics.estimated_co2_saved_kg ?? 0).toLocaleString()} kg`,
      subtext: 'Clean freight transport',
      icon: Leaf,
      color: 'from-green-500 to-emerald-700',
      textColor: 'text-green-400',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 my-6">
      {items.map((item, idx) => {
        const Icon = item.icon;
        return (
          <div
            key={idx}
            className="glass-card rounded-2xl p-5 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-blue-500/10"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
                {item.title}
              </span>
              <div className={`p-2.5 rounded-xl bg-gradient-to-br ${item.color} text-white shadow-md`}>
                <Icon className="w-5 h-5" />
              </div>
            </div>
            <div className={`text-2xl font-extrabold ${item.textColor} tracking-tight`}>
              {item.value}
            </div>
            <div className="text-xs text-slate-400 mt-1 font-medium">
              {item.subtext}
            </div>
          </div>
        );
      })}
    </div>
  );
};
