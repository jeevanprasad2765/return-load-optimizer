import React, { useEffect, useState } from 'react';
import apiClient from '../../api/client';
import { TruckForm } from '../../components/TruckForm';
import { Truck, Trash2, Weight, ShieldCheck } from 'lucide-react';

export const CarrierTrucks = () => {
  const [trucks, setTrucks] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchTrucks = async () => {
    try {
      const res = await apiClient.get('/trucks');
      setTrucks(res.data);
    } catch (err) {
      console.error('Failed to fetch trucks', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await apiClient.delete(`/trucks/${id}`);
      fetchTrucks();
    } catch (err) {
      console.error('Failed to delete truck', err);
    }
  };

  useEffect(() => {
    fetchTrucks();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-black text-slate-100 tracking-tight">Fleet Vehicles</h1>
        <p className="text-xs text-slate-400">Register and manage your carrier trucks for empty return matching</p>
      </div>

      <TruckForm onTruckCreated={fetchTrucks} />

      {/* Vehicles Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {trucks.map((truck) => (
          <div key={truck.id} className="glass-panel rounded-2xl p-5 relative group hover:border-blue-500/40 transition-all">
            <div className="flex items-center justify-between mb-3">
              <span className="px-3 py-1 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono font-bold text-sm">
                {truck.registration_number}
              </span>
              <button
                onClick={() => handleDelete(truck.id)}
                className="p-1.5 rounded-lg bg-slate-900 text-slate-500 hover:text-rose-400 transition-colors"
                title="Delete vehicle"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2 text-xs text-slate-300">
              <div className="flex items-center justify-between">
                <span className="text-slate-400 flex items-center gap-1.5"><ShieldCheck className="w-4 h-4 text-emerald-400"/> Type:</span>
                <span className="font-semibold uppercase text-slate-100">{truck.vehicle_type}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400 flex items-center gap-1.5"><Weight className="w-4 h-4 text-purple-400"/> Capacity:</span>
                <span className="font-bold text-slate-100">{truck.max_capacity_kg?.toLocaleString()} kg</span>
              </div>
              {truck.model_name && (
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Model:</span>
                  <span className="font-medium text-slate-200">{truck.model_name}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
