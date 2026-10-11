import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../../api/client';
import { MetricsCards } from '../../components/MetricsCards';
import { ChartPanel } from '../../components/ChartPanel';
import { MapView } from '../../components/MapView';
import { Route, Sparkles, RefreshCw, Globe2, PlusCircle } from 'lucide-react';

export const CarrierDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/dashboard/metrics');
      setData(res.data);
    } catch (err) {
      console.error('Failed to load dashboard metrics', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunMatching = async () => {
    try {
      await apiClient.post('/matches/find');
      fetchMetrics();
    } catch (err) {
      console.error('Matching run failed', err);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const hasActiveRoutes = data?.active_matched_routes && data.active_matched_routes.length > 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-100 tracking-tight flex items-center gap-2">
            Logistics Command Center <Sparkles className="w-5 h-5 text-blue-400" />
          </h1>
          <p className="text-xs text-slate-400">
            Real-time ROI metrics, return trip load matching, and environmental impact
          </p>
        </div>

        <button
          onClick={handleRunMatching}
          className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-all shadow-lg shadow-blue-500/20 flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Run Matching Engine
        </button>
      </div>

      {/* Key Metric Cards */}
      <MetricsCards metrics={data?.metrics} />

      {/* Map View of Active Matched Routes */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <Route className="w-5 h-5 text-blue-400" /> Active Matched Return Routes
            </h3>
            <p className="text-xs text-slate-400">Interactive OpenStreetMap display of empty trip corridors & pickups</p>
          </div>
        </div>

        {hasActiveRoutes ? (
          <MapView routes={data?.active_matched_routes || []} height="420px" />
        ) : (
          <div className="flex flex-col items-center justify-center py-16 px-4 rounded-xl border border-dashed border-slate-800 bg-slate-900/40 text-center space-y-3">
            <Route className="w-10 h-10 text-blue-400/60" />
            <div className="text-sm font-bold text-slate-200">No active matched return routes yet</div>
            <p className="text-xs text-slate-400 max-w-md">
              Post your first empty return trip to automatically discover matched cargo shipments and visualize routes on the map.
            </p>
            <Link
              to="/carrier/trips"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-500/20 transition-all"
            >
              <PlusCircle className="w-3.5 h-3.5" /> Post Return Trip
            </Link>
          </div>
        )}
      </div>

      {/* Recharts Analytics Panel */}
      <ChartPanel monthlyTrends={data?.monthly_trends} routeVolumes={data?.route_volumes} />

      {/* Optional Platform-Wide Impact (Global Totals) */}
      {data?.platform_metrics && (
        <div className="glass-panel rounded-2xl p-6 border border-slate-800/80">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-200 flex items-center gap-2">
                <Globe2 className="w-4 h-4 text-emerald-400" /> Platform-Wide Network Impact
              </h3>
              <p className="text-xs text-slate-400">
                Global aggregate savings across all active freight carriers & shippers on the platform
              </p>
            </div>
            <span className="self-start sm:self-auto px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[11px] font-semibold">
              Global Network Total
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 text-xs">
            <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-800">
              <span className="text-slate-400 block mb-1">Global Km Reduced</span>
              <span className="text-sm font-bold text-slate-100">
                {(data.platform_metrics.empty_km_reduced ?? 0).toLocaleString()} km
              </span>
            </div>
            <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-800">
              <span className="text-slate-400 block mb-1">Total Carrier Revenue</span>
              <span className="text-sm font-bold text-emerald-400">
                ₹{(data.platform_metrics.total_revenue_generated ?? 0).toLocaleString()}
              </span>
            </div>
            <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-800">
              <span className="text-slate-400 block mb-1">Total Shipper Savings</span>
              <span className="text-sm font-bold text-amber-400">
                ₹{(data.platform_metrics.total_cost_saved_shippers ?? 0).toLocaleString()}
              </span>
            </div>
            <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-800">
              <span className="text-slate-400 block mb-1">Network Capacity Util.</span>
              <span className="text-sm font-bold text-purple-400">
                {data.platform_metrics.average_vehicle_utilization_pct ?? 0}%
              </span>
            </div>
            <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-800">
              <span className="text-slate-400 block mb-1">Total CO₂ Prevented</span>
              <span className="text-sm font-bold text-green-400">
                {(data.platform_metrics.total_co2_saved_kg ?? 0).toLocaleString()} kg
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
