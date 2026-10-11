import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/Layout';
import { Login } from './pages/Login';
import { Register } from './pages/Register';

// Carrier Pages
import { CarrierDashboard } from './pages/carrier/Dashboard';
import { CarrierTrucks } from './pages/carrier/Trucks';
import { CarrierTrips } from './pages/carrier/Trips';
import { TripMatches } from './pages/carrier/TripMatches';
import { CarrierBookings } from './pages/carrier/Bookings';

// Shipper Pages
import { ShipperDashboard } from './pages/shipper/Dashboard';
import { ShipperShipments } from './pages/shipper/Shipments';
import { ShipmentMatches } from './pages/shipper/ShipmentMatches';
import { ShipperBookings } from './pages/shipper/Bookings';

const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const RoleBasedHome = () => {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;

  if (user.role === 'carrier') {
    return <CarrierDashboard />;
  }
  return <ShipperDashboard />;
};

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Application Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout>
                  <RoleBasedHome />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Carrier Specific Routes */}
          <Route
            path="/carrier/trucks"
            element={
              <ProtectedRoute>
                <Layout>
                  <CarrierTrucks />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/carrier/trips"
            element={
              <ProtectedRoute>
                <Layout>
                  <CarrierTrips />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/carrier/trips/:tripId/matches"
            element={
              <ProtectedRoute>
                <Layout>
                  <TripMatches />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/carrier/bookings"
            element={
              <ProtectedRoute>
                <Layout>
                  <CarrierBookings />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Shipper Specific Routes */}
          <Route
            path="/shipper/shipments"
            element={
              <ProtectedRoute>
                <Layout>
                  <ShipperShipments />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/shipper/shipments/:shipmentId/matches"
            element={
              <ProtectedRoute>
                <Layout>
                  <ShipmentMatches />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/shipper/bookings"
            element={
              <ProtectedRoute>
                <Layout>
                  <ShipperBookings />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Fallback Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
