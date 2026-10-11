import React, { useState } from 'react';
import apiClient from '../api/client';
import { Truck, Plus } from 'lucide-react';

export const TruckForm = ({ onTruckCreated }) => {
  const [formData, setFormData] = useState({
    registration_number: '',
    vehicle_type: 'closed',
    max_capacity_kg: '',
    model_name: '',
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    const reg = formData.registration_number.trim();
    if (!/\d{4}$/.test(reg)) {
      setError('Registration number must end with 4 digits (e.g. TN-37-R-4085)');
      return;
    }

    setLoading(true);

    try {
      const res = await apiClient.post('/trucks', {
        ...formData,
        registration_number: reg,
        max_capacity_kg: parseFloat(formData.max_capacity_kg),
      });
      setFormData({
        registration_number: '',
        vehicle_type: 'closed',
        max_capacity_kg: '',
        model_name: '',
      });
      if (onTruckCreated) onTruckCreated(res.data);
    } catch (err) {
      setError(err.response?.data?.detail?.[0]?.msg || err.response?.data?.detail || 'Failed to register truck');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="glass-panel rounded-2xl p-6 mb-6">
      <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
        <Truck className="w-5 h-5 text-blue-400" /> Register New Vehicle
      </h3>

      {error && (
        <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Reg. Number
          </label>
          <input
            type="text"
            required
            placeholder="e.g. TN-37-R-4085"
            value={formData.registration_number}
            onChange={(e) => setFormData({ ...formData, registration_number: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Vehicle Type
          </label>
          <select
            value={formData.vehicle_type}
            onChange={(e) => setFormData({ ...formData, vehicle_type: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          >
            <option value="closed">Closed Container</option>
            <option value="open">Open Body Truck</option>
            <option value="refrigerated">Refrigerated (Cold Chain)</option>
            <option value="flatbed">Flatbed</option>
            <option value="container">ISO Container Trailer</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Max Capacity (kg)
          </label>
          <input
            type="number"
            required
            min="1"
            placeholder="e.g. 6000"
            value={formData.max_capacity_kg}
            onChange={(e) => setFormData({ ...formData, max_capacity_kg: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Make / Model
          </label>
          <input
            type="text"
            placeholder="e.g. Tata Prima 2830"
            value={formData.model_name}
            onChange={(e) => setFormData({ ...formData, model_name: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      <div className="mt-4 flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-all shadow-md shadow-blue-500/20 flex items-center gap-1.5"
        >
          <Plus className="w-4 h-4" /> {loading ? 'Saving...' : 'Add Vehicle'}
        </button>
      </div>
    </form>
  );
};
