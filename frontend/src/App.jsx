import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import ExecutiveDashboard from './pages/ExecutiveDashboard';
import PassengerFlowDashboard from './pages/PassengerFlowDashboard';
import RoutePerformanceDashboard from './pages/RoutePerformanceDashboard';
import DelayDashboard from './pages/DelayDashboard';
import OccupancyDashboard from './pages/OccupancyDashboard';
import ForecastDashboard from './pages/ForecastDashboard';
import RouteMapVisualization from './pages/RouteMapVisualization';
import ReportsExport from './pages/ReportsExport';
import WhatIf from './pages/WhatIf';
import ModelComparison from './pages/ModelComparison';
import Login from './pages/Login';
import AuditTrail from './pages/AuditTrail';
import SystemHealth from './pages/SystemHealth';
import RouteManagement from './pages/RouteManagement';
import StopManagement from './pages/StopManagement';
import VehicleManagement from './pages/VehicleManagement';
import TripManagement from './pages/TripManagement';
import ScheduleManagement from './pages/ScheduleManagement';
import SparkJobs from './pages/SparkJobs';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="min-h-screen bg-slate-900 flex items-center justify-center text-slate-400">Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

const Layout = ({ children }) => (
  <div className="flex min-h-screen bg-slate-900 text-slate-100 font-sans min-w-[1024px] overflow-x-auto">
    <Sidebar />
    <main className="flex-1 ml-64 p-8 w-full max-w-[100vw]">
      {children}
    </main>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route path="/" element={<ProtectedRoute><Layout><ExecutiveDashboard /></Layout></ProtectedRoute>} />
          <Route path="/flow" element={<ProtectedRoute><Layout><PassengerFlowDashboard /></Layout></ProtectedRoute>} />
          <Route path="/routes" element={<ProtectedRoute><Layout><RoutePerformanceDashboard /></Layout></ProtectedRoute>} />
          <Route path="/delays" element={<ProtectedRoute><Layout><DelayDashboard /></Layout></ProtectedRoute>} />
          <Route path="/occupancy" element={<ProtectedRoute><Layout><OccupancyDashboard /></Layout></ProtectedRoute>} />
          <Route path="/forecast" element={<ProtectedRoute><Layout><ForecastDashboard /></Layout></ProtectedRoute>} />
          <Route path="/map" element={<ProtectedRoute><Layout><RouteMapVisualization /></Layout></ProtectedRoute>} />
          <Route path="/reports" element={<ProtectedRoute><Layout><ReportsExport /></Layout></ProtectedRoute>} />
          <Route path="/whatif" element={<ProtectedRoute><Layout><WhatIf /></Layout></ProtectedRoute>} />
          <Route path="/comparison" element={<ProtectedRoute><Layout><ModelComparison /></Layout></ProtectedRoute>} />
          <Route path="/audit" element={<ProtectedRoute><Layout><AuditTrail /></Layout></ProtectedRoute>} />
          <Route path="/health" element={<ProtectedRoute><Layout><SystemHealth /></Layout></ProtectedRoute>} />
          <Route path="/admin/routes" element={<ProtectedRoute><Layout><RouteManagement /></Layout></ProtectedRoute>} />
          <Route path="/admin/stops" element={<ProtectedRoute><Layout><StopManagement /></Layout></ProtectedRoute>} />
          <Route path="/admin/vehicles" element={<ProtectedRoute><Layout><VehicleManagement /></Layout></ProtectedRoute>} />
          <Route path="/admin/trips" element={<ProtectedRoute><Layout><TripManagement /></Layout></ProtectedRoute>} />
          <Route path="/admin/schedules" element={<ProtectedRoute><Layout><ScheduleManagement /></Layout></ProtectedRoute>} />
          <Route path="/admin/spark" element={<ProtectedRoute><Layout><SparkJobs /></Layout></ProtectedRoute>} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
