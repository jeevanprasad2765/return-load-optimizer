import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../../api/client';
import { MatchCard } from '../../components/MatchCard';
import { ConsolidationGroupCard } from '../../components/ConsolidationGroupCard';
import { Sparkles, Layers, ArrowLeft, CheckCircle } from 'lucide-react';

export const TripMatches = () => {
  const { tripId } = useParams();
  const [matches, setMatches] = useState([]);
  const [consolidation, setConsolidation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [acceptedNotice, setAcceptedNotice] = useState(false);

  const fetchMatches = async () => {
    try {
      const [matchesRes, consolidationRes] = await Promise.all([
        apiClient.get(`/trips/${tripId}/matches`),
        apiClient.get(`/trips/${tripId}/consolidation`),
      ]);
      setMatches(matchesRes.data);
      setConsolidation(consolidationRes.data);
    } catch (err) {
      console.error('Failed to fetch trip matches', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptMatch = async (matchId) => {
    try {
      await apiClient.put(`/matches/${matchId}/accept`);
      setAcceptedNotice(true);
      fetchMatches();
    } catch (err) {
      console.error('Failed to accept match', err);
    }
  };

  const handleRejectMatch = async (matchId) => {
    try {
      await apiClient.put(`/matches/${matchId}/reject`);
      fetchMatches();
    } catch (err) {
      console.error('Failed to reject match', err);
    }
  };

  const handleAcceptConsolidatedGroup = async (group) => {
    try {
      for (const m of group.matches) {
        await apiClient.post('/bookings', {
          match_id: m.id,
          trip_id: m.trip_id,
          shipment_id: m.shipment_id,
          agreed_price: m.estimated_revenue
        });
      }
      setAcceptedNotice(true);
      fetchMatches();
    } catch (err) {
      console.error('Failed to accept consolidated group', err);
    }
  };

  useEffect(() => {
    fetchMatches();
  }, [tripId]);

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/carrier/trips" className="p-2 rounded-xl bg-slate-900 text-slate-400 hover:text-white">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-black text-slate-100 tracking-tight flex items-center gap-2">
            Ranked Shipment Matches <Sparkles className="w-5 h-5 text-amber-400" />
          </h1>
          <p className="text-xs text-slate-400">Multi-factor engine scoring (Route 40%, Capacity 25%, Time 20%, Vehicle 15%)</p>
        </div>
      </div>

      {acceptedNotice && (
        <div className="p-4 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-200 text-sm font-semibold flex items-center justify-between gap-4 shadow-lg shadow-emerald-500/10 animate-fade-in">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
            <span>Match accepted successfully! Freight booking created and capacity updated.</span>
          </div>
          <Link
            to="/carrier/bookings"
            className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md transition-all whitespace-nowrap flex items-center gap-1.5"
          >
            Go to Bookings →
          </Link>
        </div>
      )}

      {/* Multi-Shipment Consolidation Groups Section */}
      {consolidation && consolidation.groups && consolidation.groups.length > 0 && (
        <div className="space-y-4 my-6">
          <h3 className="text-sm font-extrabold text-purple-300 uppercase tracking-wider flex items-center gap-2">
            <Layers className="w-4 h-4 text-purple-400" /> Multi-Shipment Consolidated Combinations ({consolidation.groups.length} Groups)
          </h3>
          {consolidation.groups.map((group) => (
            <ConsolidationGroupCard
              key={group.group_id}
              group={group}
              onAcceptGroup={handleAcceptConsolidatedGroup}
            />
          ))}
        </div>
      )}

      {/* Individual Matches List */}
      <div className="space-y-4">
        <h3 className="text-sm font-extrabold text-slate-400 uppercase tracking-wider">
          Individual Shipment Matches
        </h3>
        {loading ? (
          <div className="glass-panel rounded-2xl p-8 text-center text-slate-400 text-sm">
            Loading candidate shipment matches...
          </div>
        ) : matches.length === 0 ? (
          <div className="glass-panel rounded-2xl p-8 text-center text-slate-400 text-sm">
            No compatible matches found for this trip yet.
          </div>
        ) : (
          matches.map((match) => (
            <MatchCard
              key={match.id}
              match={match}
              onAccept={handleAcceptMatch}
              onReject={handleRejectMatch}
              isCarrier={true}
            />
          ))
        )}
      </div>
    </div>
  );
};
