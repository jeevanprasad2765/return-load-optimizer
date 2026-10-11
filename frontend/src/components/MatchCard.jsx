import React from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle, AlertCircle, ArrowRight, Route, ShieldCheck, Clock, Weight, DollarSign, AlertTriangle, Loader2, Building, Calendar, Truck } from 'lucide-react';
import { formatDateTime } from '../utils/dateUtils';

export const MatchCard = ({
  match,
  onAccept,
  onReject,
  onBook,
  isCarrier = true,
  isBooking = false,
  bookingStatus = null,
}) => {
  const {
    id, score, breakdown, is_rejected, rejection_reason,
    detour_km, detour_minutes, estimated_revenue,
    estimated_cost_shipper, cost_savings_amount, cost_savings_pct,
    is_osrm_fallback, status, trip, shipment
  } = match;

  const currentBookingStatus = bookingStatus || match.booking_status;

  const scoreColor = is_rejected
    ? 'text-rose-500 border-rose-500/30 bg-rose-500/10'
    : score >= 80
    ? 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10'
    : score >= 60
    ? 'text-amber-400 border-amber-500/30 bg-amber-500/10'
    : 'text-blue-400 border-blue-500/30 bg-blue-500/10';

  const priceShipper = estimated_cost_shipper || estimated_revenue || 0;
  const earningsCarrier = estimated_revenue || 0;

  return (
    <div className={`glass-panel rounded-2xl p-6 transition-all duration-300 relative overflow-hidden ${is_rejected ? 'opacity-75 border-rose-900/30' : 'hover:border-blue-500/40'}`}>
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4 mb-3">
        {/* Origin -> Destination Banner */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-200 text-sm font-semibold flex items-center gap-2">
            <span>{trip?.origin_name || 'Origin'}</span>
            <ArrowRight className="w-4 h-4 text-blue-400" />
            <span>{trip?.dest_name || 'Destination'}</span>
          </div>

          {shipment && (
            <div className="text-xs text-slate-400">
              Pickup: <span className="text-slate-200 font-medium">{shipment.pickup_name}</span> | Goods: <span className="text-slate-200 font-medium">{shipment.goods_type} ({shipment.weight_kg} kg)</span>
            </div>
          )}
        </div>

        {/* Match Score Badge */}
        <div className="flex items-center space-x-3">
          {is_osrm_fallback && (
            <span className="px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20 text-[11px] font-medium flex items-center gap-1" title="Straight-line Haversine estimate used due to router timeout">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> Straight-line fallback
            </span>
          )}
          <div className={`px-4 py-2 rounded-xl border font-extrabold text-lg flex items-center gap-2 ${scoreColor}`}>
            <span>{is_rejected ? 'REJECTED' : `${score}/100`}</span>
          </div>
        </div>
      </div>

      {/* Carrier & Departure distinguishing info (prevents identical card confusion) */}
      <div className="flex flex-wrap items-center gap-4 text-xs text-slate-300 mb-4 bg-slate-900/70 px-4 py-2.5 rounded-xl border border-slate-800/80">
        <div className="flex items-center gap-1.5">
          <Building className="w-3.5 h-3.5 text-blue-400" />
          <span className="text-slate-400">Carrier:</span>
          <span className="text-slate-100 font-bold">{trip?.carrier?.company_name || trip?.carrier?.full_name || 'Verified Carrier'}</span>
        </div>
        {trip?.departure_time && (
          <div className="flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-slate-400">Departure:</span>
            <span className="text-emerald-300 font-semibold">{formatDateTime(trip.departure_time)}</span>
          </div>
        )}
        {trip?.truck && (
          <div className="flex items-center gap-1.5">
            <Truck className="w-3.5 h-3.5 text-purple-400" />
            <span className="text-slate-400">Vehicle:</span>
            <span className="text-slate-200 font-medium">{trip.truck.registration_number} ({trip.truck.vehicle_type})</span>
          </div>
        )}
      </div>

      {/* Rejection Notice if applicable */}
      {is_rejected && (
        <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{rejection_reason}</span>
        </div>
      )}

      {/* Factor Breakdown Bars */}
      {!is_rejected && breakdown && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 my-4">
          <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-800">
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span className="flex items-center gap-1"><Route className="w-3.5 h-3.5 text-blue-400"/> Route (40%)</span>
              <span className="font-bold text-slate-200">{breakdown.route_score}%</span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div className="bg-blue-500 h-full rounded-full" style={{ width: `${breakdown.route_score}%` }}></div>
            </div>
          </div>

          <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-800">
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span className="flex items-center gap-1"><Weight className="w-3.5 h-3.5 text-purple-400"/> Capacity (25%)</span>
              <span className="font-bold text-slate-200">{breakdown.capacity_score}%</span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div className="bg-purple-500 h-full rounded-full" style={{ width: `${breakdown.capacity_score}%` }}></div>
            </div>
          </div>

          <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-800">
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5 text-amber-400"/> Time (20%)</span>
              <span className="font-bold text-slate-200">{breakdown.time_score}%</span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div className="bg-amber-500 h-full rounded-full" style={{ width: `${breakdown.time_score}%` }}></div>
            </div>
          </div>

          <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-800">
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span className="flex items-center gap-1"><ShieldCheck className="w-3.5 h-3.5 text-emerald-400"/> Vehicle (15%)</span>
              <span className="font-bold text-slate-200">{breakdown.vehicle_score}%</span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${breakdown.vehicle_score}%` }}></div>
            </div>
          </div>
        </div>
      )}

      {/* Details, Pricing & Savings */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-4 pt-4 border-t border-slate-800/80">
        <div className="text-xs text-slate-400 space-y-1">
          <div>OSRM Road Detour: <span className="text-slate-200 font-semibold">{detour_km} km</span> (+{detour_minutes} mins)</div>
          
          {isCarrier ? (
            <div>Estimated Earnings: <span className="text-emerald-400 font-bold text-sm">₹{earningsCarrier.toLocaleString()}</span></div>
          ) : (
            <div className="flex flex-wrap items-center gap-2">
              <span>Estimated Price: <strong className="text-amber-400 text-sm">₹{priceShipper.toLocaleString()}</strong></span>
              {cost_savings_amount > 0 && (
                <span className="px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-300 font-bold border border-emerald-500/20 text-[11px]">
                  You Save ₹{cost_savings_amount.toLocaleString()} ({cost_savings_pct}%)
                </span>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center space-x-2">
          {!is_rejected && (
            <>
              {onBook && (
                <>
                  {currentBookingStatus === 'pending' ? (
                    <span className="px-4 py-2.5 rounded-xl bg-amber-500/15 text-amber-300 border border-amber-500/30 text-xs font-bold flex items-center gap-1.5 shadow-sm">
                      <Clock className="w-4 h-4 text-amber-400" /> Requested ✓ (Pending)
                    </span>
                  ) : currentBookingStatus === 'confirmed' ? (
                    <span className="px-4 py-2.5 rounded-xl bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 text-xs font-bold flex items-center gap-1.5 shadow-sm">
                      <CheckCircle className="w-4 h-4 text-emerald-400" /> Confirmed ✓
                    </span>
                  ) : isBooking ? (
                    <button
                      disabled
                      className="px-4 py-2.5 rounded-xl bg-amber-700/80 text-white font-semibold text-xs flex items-center gap-1.5 opacity-80 cursor-not-allowed"
                    >
                      <Loader2 className="w-4 h-4 animate-spin" /> Requesting...
                    </button>
                  ) : (
                    <button
                      onClick={() => onBook(match)}
                      className="px-4 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs transition-all shadow-md shadow-amber-600/20 flex items-center gap-1.5"
                    >
                      <DollarSign className="w-4 h-4" /> Request Booking
                    </button>
                  )}
                </>
              )}
              {onAccept && (
                <button
                  onClick={() => onAccept(id)}
                  className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all shadow-md shadow-emerald-600/20 flex items-center gap-1.5"
                >
                  <CheckCircle className="w-4 h-4" /> Accept Match
                </button>
              )}
              {onReject && (
                <button
                  onClick={() => onReject(id)}
                  className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-rose-900/50 text-slate-300 hover:text-rose-300 text-xs transition-colors border border-slate-700"
                >
                  Reject
                </button>
              )}
            </>
          )}

          {status === 'accepted' && !onBook && (
            <Link
              to={isCarrier ? "/carrier/bookings" : "/shipper/bookings"}
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-1.5 shadow-md shadow-emerald-500/20 transition-all"
            >
              <CheckCircle className="w-4 h-4" /> Accepted — View in Bookings →
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};
