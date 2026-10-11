import React, { useState } from 'react';
import apiClient from '../api/client';
import { Package, Plus } from 'lucide-react';
import { toLocalDatetimeInput, localInputToUtcIso } from '../utils/dateUtils';

const TN_CITIES = {
  Chennai: { lat: 13.0827, lon: 80.2707 },
  Coimbatore: { lat: 11.0168, lon: 76.9558 },
  Madurai: { lat: 9.9252, lon: 78.1198 },
  Salem: { lat: 11.6643, lon: 78.1460 },
  Trichy: { lat: 10.7905, lon: 78.7047 },
  Tiruppur: { lat: 11.1085, lon: 77.3411 },
};

export const ShipmentForm = ({ onShipmentCreated }) => {
  const [formData, setFormData] = useState({
    pickup_name: 'Salem',
    dest_name: 'Coimbatore',
    weight_kg: '3000',
    goods_type: 'Textiles & Fabrics',
    required_vehicle_type: 'closed',
    delivery_deadline: toLocalDatetimeInput(new Date(Date.now() + 3600 * 1000 * 24)),
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const pickupCoords = TN_CITIES[formData.pickup_name] || TN_CITIES.Salem;
    const destCoords = TN_CITIES[formData.dest_name] || TN_CITIES.Coimbatore;

    try {
      const payload = {
        pickup_name: formData.pickup_name,
        pickup_lat: pickupCoords.lat,
        pickup_lon: pickupCoords.lon,
        dest_name: formData.dest_name,
        dest_lat: destCoords.lat,
        dest_lon: destCoords.lon,
        weight_kg: parseFloat(formData.weight_kg),
        goods_type: formData.goods_type,
        required_vehicle_type: formData.required_vehicle_type || null,
        delivery_deadline: localInputToUtcIso(formData.delivery_deadline),
      };

      const res = await apiClient.post('/shipments', payload);
      if (onShipmentCreated) onShipmentCreated(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to post shipment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="glass-panel rounded-2xl p-6 mb-6">
      <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
        <Package className="w-5 h-5 text-amber-400" /> Post New Shipment
      </h3>

      {error && (
        <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Pickup City
          </label>
          <select
            value={formData.pickup_name}
            onChange={(e) => setFormData({ ...formData, pickup_name: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          >
            {Object.keys(TN_CITIES).map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Destination City
          </label>
          <select
            value={formData.dest_name}
            onChange={(e) => setFormData({ ...formData, dest_name: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          >
            {Object.keys(TN_CITIES).map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Total Weight (kg)
          </label>
          <input
            type="number"
            required
            min="1"
            value={formData.weight_kg}
            onChange={(e) => setFormData({ ...formData, weight_kg: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Goods Description
          </label>
          <input
            type="text"
            required
            placeholder="e.g. Steel coil, Auto parts, Garments"
            value={formData.goods_type}
            onChange={(e) => setFormData({ ...formData, goods_type: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Required Vehicle Type
          </label>
          <select
            value={formData.required_vehicle_type}
            onChange={(e) => setFormData({ ...formData, required_vehicle_type: e.target.value })}
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
            Delivery Deadline
          </label>
          <input
            type="datetime-local"
            value={formData.delivery_deadline}
            onChange={(e) => setFormData({ ...formData, delivery_deadline: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      <div className="mt-4 flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="px-5 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs transition-all shadow-md shadow-amber-600/20 flex items-center gap-1.5"
        >
          <Plus className="w-4 h-4" /> {loading ? 'Posting...' : 'Post Shipment'}
        </button>
      </div>
    </form>
  );
};
