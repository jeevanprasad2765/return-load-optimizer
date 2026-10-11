import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import { Route, Plus, AlertCircle } from 'lucide-react';
import { toLocalDatetimeInput, localInputToUtcIso } from '../utils/dateUtils';

const TN_CITIES = {
  Chennai: { lat: 13.0827, lon: 80.2707 },
  Coimbatore: { lat: 11.0168, lon: 76.9558 },
  Madurai: { lat: 9.9252, lon: 78.1198 },
  Salem: { lat: 11.6643, lon: 78.1460 },
  Trichy: { lat: 10.7905, lon: 78.7047 },
  Tiruppur: { lat: 11.1085, lon: 77.3411 },
};

export const TripForm = ({ trucks = [], loadingTrucks = false, onTripCreated }) => {
  const [formData, setFormData] = useState(() => ({
    truck_id: trucks[0]?.id || '',
    origin_name: 'Chennai',
    dest_name: 'Coimbatore',
    departure_time: toLocalDatetimeInput(new Date(Date.now() + 3600 * 1000 * 3)),
    available_capacity_kg: '5000',
    cost_per_km: '16.0',
  }));
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Sync selected truck when trucks list loads or updates
  useEffect(() => {
    if (trucks && trucks.length > 0) {
      setFormData((prev) => {
        const currentValid = trucks.some((t) => t.id === prev.truck_id);
        if (!prev.truck_id || !currentValid) {
          const first = trucks[0];
          return {
            ...prev,
            truck_id: first.id,
            available_capacity_kg: String(first.max_capacity_kg || 5000),
          };
        }
        return prev;
      });
    }
  }, [trucks]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    const effectiveTruckId = formData.truck_id || trucks[0]?.id;
    if (!effectiveTruckId) {
      setError('Please register and select a vehicle in "My Trucks" before posting a return trip.');
      return;
    }

    setLoading(true);

    const originCoords = TN_CITIES[formData.origin_name] || TN_CITIES.Chennai;
    const destCoords = TN_CITIES[formData.dest_name] || TN_CITIES.Coimbatore;

    try {
      const payload = {
        truck_id: effectiveTruckId,
        origin_name: formData.origin_name,
        origin_lat: originCoords.lat,
        origin_lon: originCoords.lon,
        dest_name: formData.dest_name,
        dest_lat: destCoords.lat,
        dest_lon: destCoords.lon,
        departure_time: localInputToUtcIso(formData.departure_time),
        available_capacity_kg: parseFloat(formData.available_capacity_kg),
        cost_per_km: parseFloat(formData.cost_per_km),
      };

      const res = await apiClient.post('/trips', payload);
      if (onTripCreated) onTripCreated(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to post return trip');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="glass-panel rounded-2xl p-6 mb-6">
      <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
        <Route className="w-5 h-5 text-emerald-400" /> Post Empty Return Trip
      </h3>

      {error && (
        <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Select Vehicle
          </label>
          <select
            value={formData.truck_id}
            onChange={(e) => {
              const selectedTruck = trucks.find((t) => t.id === e.target.value);
              setFormData({
                ...formData,
                truck_id: e.target.value,
                available_capacity_kg: selectedTruck ? String(selectedTruck.max_capacity_kg) : formData.available_capacity_kg,
              });
            }}
            disabled={loadingTrucks || trucks.length === 0}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-blue-500 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loadingTrucks ? (
              <option value="" disabled>Loading vehicles...</option>
            ) : trucks.length === 0 ? (
              <option value="" disabled>-- No vehicles registered --</option>
            ) : (
              trucks.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.registration_number} {t.model_name ? `(${t.model_name})` : ''} • {t.vehicle_type} • {t.max_capacity_kg} kg
                </option>
              ))
            )}
          </select>
          {!loadingTrucks && trucks.length === 0 && (
            <p className="mt-1.5 text-xs text-amber-400 flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
              <span>No vehicle found.</span>
              <Link to="/carrier/trucks" className="text-blue-400 hover:text-blue-300 underline font-semibold">
                Add a truck in My Trucks
              </Link>
            </p>
          )}
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Origin City
          </label>
          <select
            value={formData.origin_name}
            onChange={(e) => setFormData({ ...formData, origin_name: e.target.value })}
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
            Departure Time
          </label>
          <input
            type="datetime-local"
            required
            value={formData.departure_time}
            onChange={(e) => setFormData({ ...formData, departure_time: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Available Capacity (kg)
          </label>
          <input
            type="number"
            required
            min="1"
            value={formData.available_capacity_kg}
            onChange={(e) => setFormData({ ...formData, available_capacity_kg: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Cost Per Km (₹)
          </label>
          <input
            type="number"
            required
            step="0.5"
            min="1"
            value={formData.cost_per_km}
            onChange={(e) => setFormData({ ...formData, cost_per_km: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      <div className="mt-4 flex justify-end">
        <button
          type="submit"
          disabled={loading || trucks.length === 0}
          title={trucks.length === 0 ? 'Please register a vehicle in My Trucks first' : 'Post Return Trip'}
          className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all shadow-md shadow-emerald-600/20 flex items-center gap-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Plus className="w-4 h-4" /> {loading ? 'Posting...' : 'Post Return Trip'}
        </button>
      </div>
    </form>
  );
};
