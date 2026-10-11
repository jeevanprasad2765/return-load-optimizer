import React, { useEffect, useState } from 'react';
import apiClient from '../../api/client';
import { StatusBadge } from '../../components/StatusBadge';
import { Package, Truck, ArrowRight, Clock, ShieldCheck, Trash2 } from 'lucide-react';
import { formatDateTime } from '../../utils/dateUtils';

export const ShipperBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchBookings = async () => {
    try {
      const res = await apiClient.get('/bookings');
      setBookings(res.data);
    } catch (err) {
      console.error('Failed to fetch shipper bookings', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteBooking = async (id) => {
    try {
      await apiClient.delete(`/bookings/${id}`);
      fetchBookings();
    } catch (err) {
      console.error('Failed to delete booking', err);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-black text-slate-100 tracking-tight flex items-center gap-2">
          Freight Bookings & Transit Tracker <Package className="w-5 h-5 text-amber-400" />
        </h1>
        <p className="text-xs text-slate-400">Track real-time status of your freight booking requests</p>
      </div>

      <div className="space-y-4">
        {bookings.length === 0 ? (
          <div className="glass-panel rounded-2xl p-8 text-center text-slate-400 text-sm">
            No active bookings yet. Request a booking from your shipment match options.
          </div>
        ) : (
          bookings.map((b) => (
            <div key={b.id} className="glass-panel rounded-2xl p-6 transition-all hover:border-slate-700">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4 mb-4">
                <div className="flex items-center space-x-3">
                  <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-100 text-sm font-bold flex items-center gap-2">
                    <span>{b.shipment?.pickup_name || 'Pickup'}</span>
                    <ArrowRight className="w-4 h-4 text-amber-400" />
                    <span>{b.shipment?.dest_name || 'Destination'}</span>
                  </div>
                  <StatusBadge status={b.status} />
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <div className="text-xs text-slate-400">Total Price</div>
                    <div className="text-lg font-extrabold text-amber-400">₹{b.agreed_price?.toLocaleString()}</div>
                  </div>
                  <button
                    onClick={() => handleDeleteBooking(b.id)}
                    className="p-2 rounded-xl bg-slate-900 hover:bg-rose-950/40 text-slate-400 hover:text-rose-400 transition-colors border border-slate-800"
                    title="Delete Booking Record"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-300">
                <div>
                  <span className="text-slate-400 block mb-0.5">Goods Description:</span>
                  <span className="font-semibold text-slate-100">{b.shipment?.goods_type} ({b.shipment?.weight_kg} kg)</span>
                </div>
                <div>
                  <span className="text-slate-400 block mb-0.5">Return Route:</span>
                  <span className="font-medium text-slate-200">{b.trip?.origin_name} → {b.trip?.dest_name}</span>
                </div>
                <div>
                  <span className="text-slate-400 block mb-0.5">Last Updated:</span>
                  <span className="font-medium text-slate-300 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-blue-400" /> {formatDateTime(b.updated_at || b.created_at)}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
