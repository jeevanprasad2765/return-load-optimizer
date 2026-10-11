import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../../api/client';
import { TripForm } from '../../components/TripForm';
import { StatusBadge } from '../../components/StatusBadge';
import { ArrowRight, Sparkles, Trash2 } from 'lucide-react';
import { formatDateTime } from '../../utils/dateUtils';

export const CarrierTrips = () => {
  const [trips, setTrips] = useState([]);
  const [trucks, setTrucks] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [tripsRes, trucksRes] = await Promise.allSettled([
        apiClient.get('/trips'),
        apiClient.get('/trucks'),
      ]);
      if (tripsRes.status === 'fulfilled') {
        setTrips(tripsRes.value.data);
      } else {
        console.error('Failed to fetch trips', tripsRes.reason);
      }
      if (trucksRes.status === 'fulfilled') {
        setTrucks(trucksRes.value.data);
      } else {
        console.error('Failed to fetch trucks', trucksRes.reason);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDeleteTrip = async (id) => {
    try {
      await apiClient.delete(`/trips/${id}`);
      fetchData();
    } catch (err) {
      console.error('Failed to delete trip', err);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-black text-slate-100 tracking-tight">Empty Return Trips</h1>
        <p className="text-xs text-slate-400">Post return routes to automatically match with pending shipments</p>
      </div>

      <TripForm trucks={trucks} loadingTrucks={loading} onTripCreated={fetchData} />

      {/* Trips List */}
      <div className="space-y-4">
        {loading ? (
          <div className="glass-panel rounded-2xl p-8 text-center text-slate-400 text-sm">
            Loading scheduled trips...
          </div>
        ) : trips.length === 0 ? (
          <div className="glass-panel rounded-2xl p-8 text-center text-slate-400 text-sm">
            No empty return trips posted yet. Use the form above to add one.
          </div>
        ) : (
          trips.map((trip) => (
          <div key={trip.id} className="glass-panel rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-2">
              <div className="flex items-center space-x-3">
                <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-100 text-sm font-bold flex items-center gap-2">
                  <span>{trip.origin_name}</span>
                  <ArrowRight className="w-4 h-4 text-emerald-400" />
                  <span>{trip.dest_name}</span>
                </div>
                <StatusBadge status={trip.status} />
              </div>

              <div className="text-xs text-slate-400 flex flex-wrap gap-4">
                <div>Departure: <span className="text-slate-200 font-medium">{formatDateTime(trip.departure_time)}</span></div>
                <div>Capacity: <span className="text-slate-200 font-medium">{trip.available_capacity_kg} kg</span></div>
                <div>Cost Rate: <span className="text-emerald-400 font-bold">₹{trip.cost_per_km}/km</span></div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Link
                to={`/carrier/trips/${trip.id}/matches`}
                className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-500/20 flex items-center gap-1.5"
              >
                <Sparkles className="w-4 h-4" /> View Matches
              </Link>
              <button
                onClick={() => handleDeleteTrip(trip.id)}
                className="p-2 rounded-xl bg-slate-900 hover:bg-rose-950/40 text-slate-400 hover:text-rose-400 transition-colors border border-slate-800"
                title="Delete Trip"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        )))}
      </div>
    </div>
  );
};
