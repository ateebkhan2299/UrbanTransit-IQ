import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Shell from './components/layout/Shell';
import Login from './pages/Login';
import Overview from './pages/Overview';
import Recommendations from './pages/Recommendations';
import RouteMap from './pages/RouteMap';
import Delays from './pages/Delays';
import Occupancy from './pages/Occupancy';
import Admin from './pages/Admin';
import PassengerFlow from './pages/PassengerFlow';
import RoutePerformance from './pages/RoutePerformance';
import Forecast from './pages/Forecast';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Shell />}>
            <Route index element={<Navigate to="/overview" replace />} />
            <Route path="overview"           element={<Overview />} />
            <Route path="passenger-flow"     element={<PassengerFlow />} />
            <Route path="route-performance"  element={<RoutePerformance />} />
            <Route path="delays"             element={<Delays />} />
            <Route path="occupancy"          element={<Occupancy />} />
            <Route path="forecast"           element={<Forecast />} />
            <Route path="recommendations"    element={<Recommendations />} />
            <Route path="map"                element={<RouteMap />} />
            <Route path="admin"              element={<Admin />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
