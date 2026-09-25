import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Shell from './components/layout/Shell';

// Auth
import Login from './pages/Login';

// Core Dashboards
import Overview          from './pages/Overview';
import ExecutiveDashboard from './pages/ExecutiveDashboard';
import PassengerFlow     from './pages/PassengerFlow';
import PassengerFlowDashboard from './pages/PassengerFlowDashboard';
import RoutePerformance  from './pages/RoutePerformance';
import RoutePerformanceDashboard from './pages/RoutePerformanceDashboard';
import Delays            from './pages/Delays';
import DelayDashboard    from './pages/DelayDashboard';
import Occupancy         from './pages/Occupancy';
import OccupancyDashboard from './pages/OccupancyDashboard';
import Forecast          from './pages/Forecast';
import ForecastDashboard from './pages/ForecastDashboard';

// Tools & Management
import Recommendations   from './pages/Recommendations';
import WhatIf            from './pages/WhatIf';
import ModelComparison   from './pages/ModelComparison';
import ReportsExport     from './pages/ReportsExport';
import RouteMap          from './pages/RouteMap';
import RouteMapVisualization from './pages/RouteMapVisualization';
import RouteManagement   from './pages/RouteManagement';
import ScheduleManagement from './pages/ScheduleManagement';
import StopManagement    from './pages/StopManagement';
import TripManagement    from './pages/TripManagement';
import VehicleManagement from './pages/VehicleManagement';

// Admin & System
import Admin             from './pages/Admin';
import AuditTrail        from './pages/AuditTrail';
import SystemHealth      from './pages/SystemHealth';
import SparkJobs         from './pages/SparkJobs';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Shell />}>
            {/* Default redirect */}
            <Route index element={<Navigate to="/overview" replace />} />

            {/* ── Executive Overview ── */}
            <Route path="overview"            element={<Overview />} />
            <Route path="executive"           element={<ExecutiveDashboard />} />

            {/* ── Passenger Flow ── */}
            <Route path="passenger-flow"      element={<PassengerFlow />} />
            <Route path="passenger-flow-detail" element={<PassengerFlowDashboard />} />

            {/* ── Route Performance ── */}
            <Route path="route-performance"   element={<RoutePerformance />} />
            <Route path="route-performance-detail" element={<RoutePerformanceDashboard />} />

            {/* ── Delay Analysis ── */}
            <Route path="delays"              element={<Delays />} />
            <Route path="delay-dashboard"     element={<DelayDashboard />} />

            {/* ── Occupancy & Crowding ── */}
            <Route path="occupancy"           element={<Occupancy />} />
            <Route path="occupancy-dashboard" element={<OccupancyDashboard />} />

            {/* ── Demand Forecast ── */}
            <Route path="forecast"            element={<Forecast />} />
            <Route path="forecast-dashboard"  element={<ForecastDashboard />} />

            {/* ── Recommendations & What-If ── */}
            <Route path="recommendations"     element={<Recommendations />} />
            <Route path="whatif"              element={<WhatIf />} />

            {/* ── Model Comparison ── */}
            <Route path="model-comparison"    element={<ModelComparison />} />

            {/* ── Reports & Export ── */}
            <Route path="reports"             element={<ReportsExport />} />

            {/* ── Map ── */}
            <Route path="map"                 element={<RouteMap />} />
            <Route path="map-detail"          element={<RouteMapVisualization />} />

            {/* ── Management ── */}
            <Route path="route-management"    element={<RouteManagement />} />
            <Route path="schedule-management" element={<ScheduleManagement />} />
            <Route path="stop-management"     element={<StopManagement />} />
            <Route path="trip-management"     element={<TripManagement />} />
            <Route path="vehicle-management"  element={<VehicleManagement />} />

            {/* ── Admin & System ── */}
            <Route path="admin"               element={<Admin />} />
            <Route path="audit-trail"         element={<AuditTrail />} />
            <Route path="system-health"       element={<SystemHealth />} />
            <Route path="spark-jobs"          element={<SparkJobs />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
