import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../../api/client';
import { ShipmentForm } from '../../components/ShipmentForm';
import { StatusBadge } from '../../components/StatusBadge';
import { Package, ArrowRight, Sparkles, Trash2 } from 'lucide-react';
import { formatDateTime } from '../../utils/dateUtils';

export const ShipperShipments = () => {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchShipments = async () => {
    try {
      const res = await apiClient.get('/shipments');
      setShipments(res.data);
    } catch (err) {
      console.error('Failed to fetch shipments', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteShipment = async (id) => {
    try {
      await apiClient.delete(`/shipments/${id}`);
      fetchShipments();
    } catch (err) {
      console.error('Failed to delete shipment', err);
    }
  };

  useEffect(() => {
    fetchShipments();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-black text-slate-100 tracking-tight">My Shipments</h1>
        <p className="text-xs text-slate-400">Post goods for transport and view empty return truck matches</p>
      </div>

      <ShipmentForm onShipmentCreated={fetchShipments} />

      <div className="space-y-4">
        {shipments.map((shipment) => (
          <div key={shipment.id} className="glass-panel rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-2">
              <div className="flex items-center space-x-3">
                <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-100 text-sm font-bold flex items-center gap-2">
                  <span>{shipment.pickup_name}</span>
                  <ArrowRight className="w-4 h-4 text-amber-400" />
                  <span>{shipment.dest_name}</span>
                </div>
                <StatusBadge status={shipment.status} />
              </div>

              <div className="text-xs text-slate-400 flex flex-wrap gap-4">
                <div>Goods: <span className="text-slate-200 font-medium">{shipment.goods_type}</span></div>
                <div>Weight: <span className="text-slate-200 font-medium">{shipment.weight_kg} kg</span></div>
                <div>Vehicle Req: <span className="text-purple-400 font-semibold uppercase">{shipment.required_vehicle_type || 'Any'}</span></div>
                {shipment.delivery_deadline && (
                  <div>Deadline: <span className="text-slate-200 font-medium">{formatDateTime(shipment.delivery_deadline)}</span></div>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Link
                to={`/shipper/shipments/${shipment.id}/matches`}
                className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold shadow-md shadow-amber-600/20 flex items-center gap-1.5"
              >
                <Sparkles className="w-4 h-4" /> View Truck Matches
              </Link>
              <button
                onClick={() => handleDeleteShipment(shipment.id)}
                className="p-2 rounded-xl bg-slate-900 hover:bg-rose-950/40 text-slate-400 hover:text-rose-400 transition-colors border border-slate-800"
                title="Delete Shipment"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
