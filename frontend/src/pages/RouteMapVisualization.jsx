import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { getDashboardRouteGeo } from '../api/client';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { Map, Layers } from 'lucide-react';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const getRouteColor = (status, overlayType) => {
  if (overlayType === 'delay') {
    if (status === 'high') return '#ef4444'; // Red
    if (status === 'moderate') return '#f59e0b'; // Amber
    return '#10b981'; // Green
  }
  if (overlayType === 'occupancy') {
    if (status === 'high') return '#8b5cf6'; // Purple
    if (status === 'moderate') return '#06b6d4'; // Cyan
    return '#3b82f6'; // Blue
  }
  return '#64748b'; // Default Slate
};

const RouteMapVisualization = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [overlay, setOverlay] = useState('delay'); // 'delay', 'occupancy', 'flow'

  useEffect(() => {
    setLoading(true);
    getDashboardRouteGeo()
      .then(res => setData(res.data))
      .catch(err => {
        console.error("Map API not ready:", err);
        setData(null);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex flex-col h-full min-h-screen">
      <Header
        title="Route Geo-Spatial Visualization"
        subtitle="Interactive map of transit routes, stops, and operational overlays"
      />

      {loading ? (
        <div className="p-8 text-center text-slate-400 glass-card">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full mb-2"></div>
          <p>Loading geographical data from pipeline...</p>
        </div>
      ) : !data || (!data.routes && !data.stops) ? (
        <div className="p-12 text-center text-slate-400 glass-card flex flex-col items-center">
          <Map className="w-12 h-12 mb-4 text-slate-500" />
          <h3 className="text-lg font-bold text-white mb-2">No map data available yet</h3>
          <p>Run the PySpark analytics pipeline to compute spatial RouteGeo data.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 mb-8">
          {/* Controls Panel */}
          <div className="glass-card p-6 lg:col-span-1 h-fit">
            <div className="flex items-center gap-2 mb-6">
              <Layers className="w-5 h-5 text-cyan-400" />
              <h3 className="text-lg font-bold text-white">Map Overlays</h3>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-bold text-slate-300 mb-2">Active Metric Overlay</label>
                <div className="space-y-2">
                  <label className="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-800/50">
                    <input 
                      type="radio" 
                      name="overlay" 
                      value="delay" 
                      checked={overlay === 'delay'} 
                      onChange={() => setOverlay('delay')}
                      className="accent-cyan-400"
                    />
                    <span className="text-slate-300">Delay Hotspots</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-800/50">
                    <input 
                      type="radio" 
                      name="overlay" 
                      value="occupancy" 
                      checked={overlay === 'occupancy'} 
                      onChange={() => setOverlay('occupancy')}
                      className="accent-cyan-400"
                    />
                    <span className="text-slate-300">Overcrowding Risk</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-800/50">
                    <input 
                      type="radio" 
                      name="overlay" 
                      value="flow" 
                      checked={overlay === 'flow'} 
                      onChange={() => setOverlay('flow')}
                      className="accent-cyan-400"
                    />
                    <span className="text-slate-300">Passenger Flow Density</span>
                  </label>
                </div>
              </div>

              <div className="mt-8 border-t border-slate-700 pt-4">
                <label className="block text-sm font-bold text-slate-300 mb-2">Legend</label>
                <div className="space-y-2 text-xs text-slate-400">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-red-500"></div>
                    <span>High {overlay === 'delay' ? 'Delay' : 'Occupancy'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-amber-500"></div>
                    <span>Moderate {overlay === 'delay' ? 'Delay' : 'Occupancy'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-emerald-500"></div>
                    <span>Normal Operation</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Map Container */}
          <div className="glass-card p-2 lg:col-span-3 min-h-[500px] z-0 overflow-hidden relative">
            <iframe
              width="100%"
              height="100%"
              style={{ border: 0, borderRadius: '0.5rem', minHeight: '500px' }}
              loading="lazy"
              allowFullScreen
              referrerPolicy="no-referrer-when-downgrade"
              src={`https://maps.google.com/maps?q=Public+Transit+Routes+New+York&t=&z=12&ie=UTF8&iwloc=&output=embed`}
            ></iframe>
          </div>
        </div>
      )}
    </div>
  );
};

export default RouteMapVisualization;
