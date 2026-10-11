import React, { useEffect, useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import apiClient from '../api/client';
import { formatDateTime } from '../utils/dateUtils';
import { Truck, Package, LogOut, LayoutDashboard, Route, CheckCircle, Bell, Check, Clock } from 'lucide-react';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const notifRef = useRef(null);

  const fetchNotifications = async () => {
    if (!user) return;
    try {
      const res = await apiClient.get('/notifications');
      setNotifications(res.data || []);
    } catch (err) {
      // Silently catch in navbar poll
    }
  };

  useEffect(() => {
    if (!user) return;
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 15000);
    return () => clearInterval(interval);
  }, [user]);

  // Click outside listener for notification popup
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setShowNotifications(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const handleMarkAsRead = async (id, relatedEntityId) => {
    try {
      await apiClient.patch(`/notifications/${id}/read`);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setShowNotifications(false);
      if (user?.role === 'carrier') {
        navigate('/carrier/bookings');
      } else {
        navigate('/shipper/bookings');
      }
    } catch (err) {
      console.error('Failed to mark notification read', err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await apiClient.post('/notifications/read-all');
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch (err) {
      console.error('Failed to mark all notifications read', err);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="glass-panel sticky top-0 z-50 border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center space-x-3 group">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
            <Route className="w-6 h-6" />
          </div>
          <div>
            <span className="text-lg font-black tracking-tight text-white group-hover:text-blue-400 transition-colors">
              ReturnLoad<span className="text-blue-500">.Optimizer</span>
            </span>
            <span className="block text-[10px] text-slate-400 font-medium tracking-widest uppercase -mt-1">
              Tamil Nadu Freight Corridor
            </span>
          </div>
        </Link>

        {/* User Navigation Links */}
        {user ? (
          <div className="flex items-center space-x-4 sm:space-x-6">
            <nav className="hidden md:flex items-center space-x-1">
              <Link
                to="/"
                className="px-3 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/80 transition-all flex items-center gap-1.5"
              >
                <LayoutDashboard className="w-4 h-4 text-blue-400" /> Dashboard
              </Link>

              {user.role === 'carrier' ? (
                <>
                  <Link
                    to="/carrier/trucks"
                    className="px-3 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/80 transition-all flex items-center gap-1.5"
                  >
                    <Truck className="w-4 h-4 text-purple-400" /> My Trucks
                  </Link>
                  <Link
                    to="/carrier/trips"
                    className="px-3 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/80 transition-all flex items-center gap-1.5"
                  >
                    <Route className="w-4 h-4 text-emerald-400" /> Return Trips
                  </Link>
                  <Link
                    to="/carrier/bookings"
                    className="px-3 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/80 transition-all flex items-center gap-1.5"
                  >
                    <CheckCircle className="w-4 h-4 text-teal-400" /> Bookings
                  </Link>
                </>
              ) : (
                <>
                  <Link
                    to="/shipper/shipments"
                    className="px-3 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/80 transition-all flex items-center gap-1.5"
                  >
                    <Package className="w-4 h-4 text-amber-400" /> My Shipments
                  </Link>
                  <Link
                    to="/shipper/bookings"
                    className="px-3 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/80 transition-all flex items-center gap-1.5"
                  >
                    <CheckCircle className="w-4 h-4 text-teal-400" /> Bookings
                  </Link>
                </>
              )}
            </nav>

            {/* Notification Bell */}
            <div className="relative" ref={notifRef}>
              <button
                onClick={() => setShowNotifications((prev) => !prev)}
                className="relative p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white transition-colors border border-slate-800"
                title="Notifications"
              >
                <Bell className="w-4 h-4" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-rose-500 text-white rounded-full text-[10px] font-black w-4 h-4 flex items-center justify-center animate-pulse">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </button>

              {/* Notifications Dropdown */}
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl z-50 overflow-hidden backdrop-blur-xl">
                  <div className="p-3.5 border-b border-slate-800 flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-100 flex items-center gap-1.5">
                      <Bell className="w-3.5 h-3.5 text-blue-400" /> Notifications
                      {unreadCount > 0 && (
                        <span className="px-1.5 py-0.5 rounded-full bg-blue-500/20 text-blue-400 text-[10px] font-bold">
                          {unreadCount} new
                        </span>
                      )}
                    </span>
                    {unreadCount > 0 && (
                      <button
                        onClick={handleMarkAllRead}
                        className="text-[11px] font-semibold text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1"
                      >
                        <Check className="w-3 h-3" /> Mark all read
                      </button>
                    )}
                  </div>

                  <div className="max-h-80 overflow-y-auto divide-y divide-slate-800/60">
                    {notifications.length === 0 ? (
                      <div className="p-6 text-center text-xs text-slate-400">
                        No notifications yet.
                      </div>
                    ) : (
                      notifications.map((n) => (
                        <div
                          key={n.id}
                          onClick={() => handleMarkAsRead(n.id, n.related_entity_id)}
                          className={`p-3 text-xs transition-colors cursor-pointer hover:bg-slate-800/60 flex items-start gap-2.5 ${
                            !n.is_read ? 'bg-blue-950/20' : 'opacity-75'
                          }`}
                        >
                          <div
                            className={`w-2 h-2 rounded-full mt-1 flex-shrink-0 ${
                              !n.is_read ? 'bg-blue-400 ring-2 ring-blue-400/30' : 'bg-transparent'
                            }`}
                          />
                          <div className="flex-1 space-y-1">
                            <p className="text-slate-200 font-medium leading-relaxed">
                              {n.message}
                            </p>
                            <span className="text-[10px] text-slate-400 flex items-center gap-1">
                              <Clock className="w-3 h-3 text-slate-500" />
                              {formatDateTime(n.created_at)}
                            </span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center space-x-3 border-l border-slate-800 pl-4">
              <div className="text-right hidden sm:block">
                <div className="text-xs font-bold text-slate-100">{user.company_name}</div>
                <div className="text-[10px] text-blue-400 uppercase tracking-wider font-semibold">
                  {user.role}
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="p-2 rounded-xl bg-slate-800 hover:bg-rose-900/40 text-slate-300 hover:text-rose-400 transition-colors border border-slate-700"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        ) : (
          <div className="flex items-center space-x-3">
            <Link
              to="/login"
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-500/20 transition-all"
            >
              Get Started
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};
