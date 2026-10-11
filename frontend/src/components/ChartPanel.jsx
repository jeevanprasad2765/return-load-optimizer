import React from 'react';
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts';
import { TrendingUp, Truck } from 'lucide-react';

export const ChartPanel = ({ monthlyTrends = [], routeVolumes = [] }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 my-6">
      {/* Monthly Trends Line Chart */}
      <div className="glass-panel rounded-2xl p-6">
        <h3 className="text-lg font-bold text-slate-100 mb-1">Impact & Revenue Trends</h3>
        <p className="text-xs text-slate-400 mb-6">Empty kilometers saved and extra revenue generated over time</p>
        
        {monthlyTrends && monthlyTrends.length > 0 ? (
          <div style={{ width: '100%', height: '320px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthlyTrends} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="month" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
                <Legend />
                <Line type="monotone" dataKey="empty_km_reduced" name="Empty Km Saved" stroke="#3b82f6" strokeWidth={3} activeDot={{ r: 8 }} />
                <Line type="monotone" dataKey="revenue" name="Revenue (₹)" stroke="#10b981" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-[320px] rounded-xl border border-dashed border-slate-800 bg-slate-900/40 text-center p-6 space-y-2">
            <TrendingUp className="w-8 h-8 text-slate-500" />
            <div className="text-sm font-semibold text-slate-300">No trend data available yet</div>
            <p className="text-xs text-slate-400 max-w-xs">
              Complete your first delivered or in-transit booking to see your monthly impact trends here.
            </p>
          </div>
        )}
      </div>

      {/* Corridor Volumes Bar Chart */}
      <div className="glass-panel rounded-2xl p-6">
        <h3 className="text-lg font-bold text-slate-100 mb-1">Corridor Freight Volumes</h3>
        <p className="text-xs text-slate-400 mb-6">Total freight tonnage moved by return load matching</p>
        
        {routeVolumes && routeVolumes.length > 0 ? (
          <div style={{ width: '100%', height: '320px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={routeVolumes} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="route" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
                <Legend />
                <Bar dataKey="volume_tons" name="Volume (Tons)" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-[320px] rounded-xl border border-dashed border-slate-800 bg-slate-900/40 text-center p-6 space-y-2">
            <Truck className="w-8 h-8 text-slate-500" />
            <div className="text-sm font-semibold text-slate-300">No corridor volume data yet</div>
            <p className="text-xs text-slate-400 max-w-xs">
              Freight tonnage moved on return trips will appear here once bookings are in transit or delivered.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
