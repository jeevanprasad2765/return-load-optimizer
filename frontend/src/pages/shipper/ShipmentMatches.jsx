import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../../api/client';
import { MatchCard } from '../../components/MatchCard';
import { Toast } from '../../components/Toast';
import { Sparkles, ArrowLeft, CheckCircle, Package } from 'lucide-react';

export const ShipmentMatches = () => {
  const { shipmentId } = useParams();
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [acceptedNotice, setAcceptedNotice] = useState(false);
  const [bookingInProgress, setBookingInProgress] = useState({});
  const [bookingStatuses, setBookingStatuses] = useState({});
  const [toast, setToast] = useState(null);

  const fetchMatchesAndBookings = async () => {
    try {
      const [matchesRes, bookingsRes] = await Promise.all([
        apiClient.get(`/shipments/${shipmentId}/matches`),
        apiClient.get('/bookings'),
      ]);

      setMatches(matchesRes.data);

      // Pre-fill existing booking statuses for this shipment
      const statusMap = {};
      const relevantBookings = (bookingsRes.data || []).filter(
        (b) => b.shipment_id === shipmentId
      );

      for (const b of relevantBookings) {
        if (b.match_id) {
          statusMap[b.match_id] = b.status;
        }
        // Also map by trip_id
        for (const m of matchesRes.data) {
          if (m.trip_id === b.trip_id) {
            statusMap[m.id] = b.status;
          }
        }
      }

      setBookingStatuses(statusMap);
    } catch (err) {
      console.error('Failed to fetch shipment matches and bookings', err);
      setToast({
        message: err.response?.data?.detail || 'Failed to load return truck matches',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleBook = async (match) => {
    const matchId = match.id;
    if (bookingInProgress[matchId]) return;

    setBookingInProgress((prev) => ({ ...prev, [matchId]: true }));

    try {
      const payload = {
        match_id: match.id,
        trip_id: match.trip_id,
        shipment_id: match.shipment_id || shipmentId,
        agreed_price: match.estimated_cost_shipper || match.estimated_revenue || null,
      };

      const res = await apiClient.post('/bookings', payload);

      // Immediately update state on success
      setBookingStatuses((prev) => ({ ...prev, [matchId]: 'pending' }));
      setAcceptedNotice(true);
      setToast({
        message: 'Booking request sent to carrier',
        type: 'success',
      });

      // Re-fetch matches to sync live state
      fetchMatchesAndBookings();
    } catch (err) {
      console.error('Failed to book truck', err);
      const errorMsg =
        err.response?.data?.detail ||
        (err.response?.status === 409
          ? 'A booking request for this return trip already exists'
          : 'Failed to submit booking request');

      if (err.response?.status === 409) {
        setBookingStatuses((prev) => ({ ...prev, [matchId]: 'pending' }));
      }

      setToast({
        message: errorMsg,
        type: 'error',
      });
    } finally {
      setBookingInProgress((prev) => ({ ...prev, [matchId]: false }));
    }
  };

  useEffect(() => {
    fetchMatchesAndBookings();
  }, [shipmentId]);

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {/* Header */}
      <div className="flex items-center space-x-3">
        <Link
          to="/shipper/shipments"
          className="p-2 rounded-xl bg-slate-900 text-slate-400 hover:text-white transition-colors border border-slate-800"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-black text-slate-100 tracking-tight flex items-center gap-2">
            Available Return Truck Matches <Sparkles className="w-5 h-5 text-blue-400" />
          </h1>
          <p className="text-xs text-slate-400">
            Ranked by route detour compatibility, vehicle type, and departure window
          </p>
        </div>
      </div>

      {/* Success banner after booking */}
      {acceptedNotice && (
        <div className="p-4 rounded-2xl bg-amber-500/20 border border-amber-500/40 text-amber-200 text-sm font-semibold flex items-center justify-between gap-4 shadow-lg shadow-amber-500/10">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-amber-400 flex-shrink-0" />
            <span>Booking request submitted! View live status updates in your Freight Bookings tab.</span>
          </div>
          <Link
            to="/shipper/bookings"
            className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs shadow-md transition-all whitespace-nowrap flex items-center gap-1.5"
          >
            Go to Freight Bookings →
          </Link>
        </div>
      )}

      {/* Matches List */}
      <div className="space-y-4">
        {loading ? (
          <div className="glass-panel rounded-2xl p-8 text-center text-slate-400 text-sm">
            Scanning available empty return trucks on this freight corridor...
          </div>
        ) : matches.length === 0 ? (
          <div className="glass-panel rounded-2xl p-8 text-center text-slate-400 text-sm">
            No matching return trucks found for this shipment right now. Try adjusting your shipment window or check back later!
          </div>
        ) : (
          matches.map((match) => (
            <MatchCard
              key={match.id}
              match={match}
              onBook={handleBook}
              isCarrier={false}
              isBooking={!!bookingInProgress[match.id]}
              bookingStatus={bookingStatuses[match.id] || match.booking_status}
            />
          ))
        )}
      </div>
    </div>
  );
};
