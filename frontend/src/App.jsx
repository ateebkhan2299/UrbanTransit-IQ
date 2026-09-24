import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Shell from './components/layout/Shell';
import Login from './pages/Login';
import Overview from './pages/Overview';
import Recommendations from './pages/Recommendations';
import RouteMap from './pages/RouteMap';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Shell />}>
            <Route index element={<Navigate to="/overview" replace />} />
            <Route path="overview" element={<Overview />} />
            <Route path="recommendations" element={<Recommendations />} />
            <Route path="map" element={<RouteMap />} />
            {/* Other routes omitted for brevity in scaffolding */}
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
