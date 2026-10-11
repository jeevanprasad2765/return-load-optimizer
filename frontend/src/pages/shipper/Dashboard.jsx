import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../../api/client';
import { MetricsCards } from '../../components/MetricsCards';
import { MapView } from '../../components/MapView';
import { Package, Sparkles, Route, Globe2, PlusCircle } from 'lucide-react';

export const ShipperDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await apiClient.get('/dashboard/metrics');
        setData(res.data);
      } catch (err) {
        console.error('Failed to load shipper metrics', err);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  const hasActiveRoutes = data?.active_matched_routes && data.active_matched_routes.length > 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-black text-slate-100 tracking-tight flex items-center gap-2">
          Shipper Logistics Hub <Package className="w-5 h-5 text-amber-400" />
        </h1>
        <p className="text-xs text-slate-400">Save up to 30% on freight costs by utilizing trucks' empty return trips</p>
      </div>

      <MetricsCards metrics={data?.metrics} />

      <div className="glass-panel rounded-2xl p-6">
        <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
          <Route className="w-5 h-5 text-amber-400" /> Active Freight Corridors
        </h3>

        {hasActiveRoutes ? (
          <MapView routes={data?.active_matched_routes || []} height="400px" />
        ) : (
          <div className="flex flex-col items-center justify-center py-16 px-4 rounded-xl border border-dashed border-slate-800 bg-slate-900/40 text-center space-y-3">
            <Package className="w-10 h-10 text-amber-400/60" />
            <div className="text-sm font-bold text-slate-200">No active freight corridors yet</div>
            <p className="text-xs text-slate-400 max-w-md">
              Post your first shipment to see matched return trucks, pickup detours, and active freight corridors on the map.
            </p>
            <Link
              to="/shipper/shipments"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold shadow-md shadow-amber-600/20 transition-all"
            >
              <PlusCircle className="w-3.5 h-3.5" /> Post Shipment
            </Link>
          </div>
        )}
      </div>

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
