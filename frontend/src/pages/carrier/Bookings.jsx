import React, { useEffect, useState } from 'react';
import apiClient from '../../api/client';
import { StatusBadge } from '../../components/StatusBadge';
import { CheckCircle, XCircle, Truck, Package, ArrowRight, DollarSign, Clock, Trash2 } from 'lucide-react';
import { formatDateTime } from '../../utils/dateUtils';

export const CarrierBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchBookings = async () => {
    try {
      const res = await apiClient.get('/bookings');
      setBookings(res.data);
    } catch (err) {
      console.error('Failed to fetch bookings', err);
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

  const handleUpdateStatus = async (bookingId, newStatus, price = null) => {
    try {
      const payload = { status: newStatus };
      if (price !== null) payload.agreed_price = price;
      await apiClient.patch(`/bookings/${bookingId}/status`, payload);
      fetchBookings();
    } catch (err) {
      console.error('Failed to update booking status', err);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-black text-slate-100 tracking-tight flex items-center gap-2">
          Freight Booking Lifecycle <Truck className="w-5 h-5 text-teal-400" />
        </h1>
        <p className="text-xs text-slate-400">Manage booking requests and update transit status (Pending → Confirmed → In Transit → Delivered)</p>
      </div>

      <div className="space-y-4">
        {bookings.length === 0 ? (
          <div className="glass-panel rounded-2xl p-8 text-center text-slate-400 text-sm">
            No freight bookings yet. Matches will appear here when shippers request bookings.
          </div>
        ) : (
          bookings.map((b) => (
            <div key={b.id} className="glass-panel rounded-2xl p-6 transition-all hover:border-slate-700">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4 mb-4">
                <div className="flex items-center space-x-3">
                  <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-100 text-sm font-bold flex items-center gap-2">
                    <span>{b.trip?.origin_name || 'Origin'}</span>
                    <ArrowRight className="w-4 h-4 text-blue-400" />
                    <span>{b.trip?.dest_name || 'Destination'}</span>
                  </div>
                  <StatusBadge status={b.status} />
                </div>

                <div className="text-right">
                  <div className="text-xs text-slate-400">Agreed Price</div>
                  <div className="text-lg font-extrabold text-emerald-400">₹{b.agreed_price?.toLocaleString()}</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-300 mb-4">
                <div>
                  <span className="text-slate-400 block mb-0.5">Cargo Goods:</span>
                  <span className="font-semibold text-slate-100 flex items-center gap-1">
                    <Package className="w-3.5 h-3.5 text-amber-400" /> {b.shipment?.goods_type} ({b.shipment?.weight_kg} kg)
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block mb-0.5">Pickup & Destination:</span>
                  <span className="font-medium text-slate-200">
                    {b.shipment?.pickup_name} → {b.shipment?.dest_name}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block mb-0.5">Booking Requested:</span>
                  <span className="font-medium text-slate-300 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-blue-400" /> {formatDateTime(b.created_at)}
                  </span>
                </div>
              </div>

              {/* Action Toolbar */}
              <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-800/80">
                {b.status === 'pending' && (
                  <>
                    <button
                      onClick={() => handleUpdateStatus(b.id, 'confirmed', b.agreed_price)}
                      className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition-all shadow-md shadow-emerald-600/20 flex items-center gap-1.5"
                    >
                      <CheckCircle className="w-4 h-4" /> Accept & Confirm Booking
                    </button>
                    <button
                      onClick={() => handleUpdateStatus(b.id, 'cancelled')}
                      className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-rose-900/50 text-slate-300 hover:text-rose-300 text-xs transition-colors border border-slate-700"
                    >
                      Decline Request
                    </button>
                  </>
                )}

                {b.status === 'confirmed' && (
                  <button
                    onClick={() => handleUpdateStatus(b.id, 'in_transit')}
                    className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs transition-all shadow-md shadow-amber-600/20 flex items-center gap-1.5"
                  >
                    Mark as In Transit
                  </button>
                )}

                {b.status === 'in_transit' && (
                  <button
                    onClick={() => handleUpdateStatus(b.id, 'delivered')}
                    className="px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs transition-all shadow-md shadow-teal-600/20 flex items-center gap-1.5"
                  >
                    <CheckCircle className="w-4 h-4" /> Mark as Delivered
                  </button>
                )}

                <button
                  onClick={() => handleDeleteBooking(b.id)}
                  className="p-2 rounded-xl bg-slate-900 hover:bg-rose-950/40 text-slate-400 hover:text-rose-400 transition-colors border border-slate-800"
                  title="Delete Booking Record"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
