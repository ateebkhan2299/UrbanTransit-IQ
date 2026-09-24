import React, { useEffect, useState } from 'react';
import Header from '../components/Header';
import { getRoutesGeo, getDelayHotspots, getRouteById } from '../api/client';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { MapPin, AlertTriangle, Activity, Users, Clock, Filter, Eye } from 'lucide-react';

// Fix default leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const RouteMap = () => {
  const [selectedRouteId, setSelectedRouteId] = useState(null);
  const [routesGeo, setRoutesGeo] = useState([]);
  const [hotspots, setHotspots] = useState([]);
  const [routeDetail, setRouteDetail] = useState(null);
  const [showHotspots, setShowHotspots] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([getRoutesGeo(), getDelayHotspots()])
      .then(([geoRes, hotRes]) => {
        setRoutesGeo(geoRes.data);
        setHotspots(hotRes.data);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (selectedRouteId) {
      getRouteById(selectedRouteId)
        .then((res) => setRouteDetail(res.data))
        .catch((err) => console.error(err));
    } else {
      setRouteDetail(null);
    }
  }, [selectedRouteId]);

  const getStatusColorHex = (status) => {
    if (status === 'high') return '#ef4444'; // Red
    if (status === 'moderate') return '#f59e0b'; // Yellow/Amber
    return '#10b981'; // Green (Normal)
  };

  // Find center coordinates from first available route path
  let center = [40.7128, -74.0060];
  if (routesGeo.length > 0 && routesGeo[0].path && routesGeo[0].path.length > 0) {
    center = [routesGeo[0].path[0].lat, routesGeo[0].path[0].lon];
  }

  const activeRoutes = selectedRouteId
    ? routesGeo.filter((r) => r.route_id === selectedRouteId)
    : routesGeo;

  return (
    <div>
      <Header
        title="Interactive Transit Route Map"
        subtitle="Geospatial route lines color-coded by performance status with bottleneck hotspot overlay"
        selectedRouteId={selectedRouteId}
        onSelectRoute={setSelectedRouteId}
      />

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Map Container */}
        <div className="flex-1 glass-card p-4 h-[600px] overflow-hidden relative rounded-xl flex flex-col">
          <div className="flex items-center justify-between pb-3 mb-2 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <MapPin className="w-5 h-5 text-cyan-400" />
              <span className="text-sm font-semibold text-slate-200">
                {selectedRouteId ? `Showing Route ${selectedRouteId}` : 'Showing All System Routes'}
              </span>
            </div>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
                <input
                  type="checkbox"
                  checked={showHotspots}
                  onChange={(e) => setShowHotspots(e.target.checked)}
                  className="rounded border-slate-600 text-cyan-500 focus:ring-cyan-400"
                />
                <Eye className="w-3.5 h-3.5 text-amber-400" />
                <span>Show Delay Hotspots Overlay</span>
              </label>
            </div>
          </div>

          {loading ? (
            <div className="flex-1 flex items-center justify-center text-slate-400">
              <div className="animate-spin inline-block w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full mr-3"></div>
              <span>Loading Geospatial Route Data...</span>
            </div>
          ) : (
            <div className="flex-1 relative rounded-lg overflow-hidden">
              <MapContainer center={center} zoom={12} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {/* Render Route Polylines */}
                {activeRoutes.map((route) => {
                  const polyCoords = route.path.map((pt) => [pt.lat, pt.lon]);
                  const color = getStatusColorHex(route.status_color);
                  const isSelected = selectedRouteId === route.route_id;

                  return (
                    <React.Fragment key={route.route_id}>
                      <Polyline
                        positions={polyCoords}
                        color={color}
                        weight={isSelected ? 7 : 4}
                        opacity={isSelected ? 0.95 : 0.75}
                        eventHandlers={{
                          click: () => setSelectedRouteId(route.route_id),
                        }}
                      >
                        <Popup>
                          <div className="text-slate-900 font-sans p-1">
                            <strong className="text-sm text-cyan-900">{route.route_name}</strong>
                            <div className="text-xs text-slate-700 mt-1">Route ID: {route.route_id}</div>
                            <div className="text-xs font-semibold mt-1" style={{ color }}>
                              Status: {route.status_color?.toUpperCase()}
                            </div>
                            <button
                              onClick={() => setSelectedRouteId(route.route_id)}
                              className="mt-2 text-xs bg-cyan-700 text-white px-2 py-1 rounded hover:bg-cyan-800"
                            >
                              Inspect Details
                            </button>
                          </div>
                        </Popup>
                      </Polyline>

                      {/* Render Stop Markers */}
                      {route.path.map((stop, idx) => (
                        <Marker key={`${route.route_id}-stop-${idx}`} position={[stop.lat, stop.lon]}>
                          <Popup>
                            <div className="text-slate-900 font-sans">
                              <strong className="text-xs">{stop.stop_name}</strong>
                              <div className="text-[10px] text-slate-600">Route: {route.route_name}</div>
                            </div>
                          </Popup>
                        </Marker>
                      ))}
                    </React.Fragment>
                  );
                })}

                {/* Hotspot Overlay */}
                {showHotspots &&
                  hotspots.map((hs) => (
                    <CircleMarker
                      key={hs.stop_id}
                      center={[hs.latitude, hs.longitude]}
                      radius={Math.min(Math.max(hs.delay_events * 2, 8), 24)}
                      pathOptions={{
                        color: '#ef4444',
                        fillColor: '#ef4444',
                        fillOpacity: 0.5,
                      }}
                    >
                      <Popup>
                        <div className="text-slate-900 font-sans">
                          <strong className="text-sm text-red-600">Delay Hotspot</strong>
                          <div className="text-xs font-bold mt-1">{hs.stop_name}</div>
                          <div className="text-xs text-slate-700">Delay Events: {hs.delay_events}</div>
                        </div>
                      </Popup>
                    </CircleMarker>
                  ))}
              </MapContainer>
            </div>
          )}
        </div>

        {/* Route Live Detail Side Panel */}
        <div className="w-full lg:w-80 glass-card p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold text-white pb-3 border-b border-slate-800 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-cyan-400" />
              <span>Route Detail Panel</span>
            </h3>

            {routeDetail ? (
              <div className="space-y-4">
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700">
                  <div className="text-xs text-slate-400 uppercase tracking-wider">Selected Route</div>
                  <div className="text-lg font-extrabold text-cyan-400 mt-1">{routeDetail.route_name}</div>
                  <div className="text-xs text-slate-400 mt-0.5">ID: {routeDetail.route_id}</div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-800/40 p-3 rounded-lg border border-slate-700/50">
                    <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
                      <Clock className="w-3.5 h-3.5 text-amber-400" />
                      <span>Avg Delay</span>
                    </div>
                    <div className="text-lg font-bold text-amber-400">{routeDetail.avg_delay_minutes} min</div>
                  </div>

                  <div className="bg-slate-800/40 p-3 rounded-lg border border-slate-700/50">
                    <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
                      <Users className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Occupancy</span>
                    </div>
                    <div className="text-lg font-bold text-cyan-400">{routeDetail.occupancy_pct}%</div>
                  </div>
                </div>

                <div className="bg-slate-800/40 p-4 rounded-lg border border-slate-700/50 space-y-3">
                  <div>
                    <div className="text-xs text-slate-400">On-Time Performance</div>
                    <div className="text-base font-bold text-emerald-400 mt-0.5">{routeDetail.on_time_pct}%</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-400">Performance Status Category</div>
                    <span className="inline-block mt-1 px-2.5 py-1 text-xs font-bold rounded-md bg-cyan-950 text-cyan-400 border border-cyan-800">
                      {routeDetail.performance_category}
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-slate-400">
                <MapPin className="w-10 h-10 mx-auto text-slate-600 mb-3" />
                <p className="text-sm">Select any route from the dropdown or click a line on the map to inspect live operational stats.</p>
              </div>
            )}
          </div>

          {selectedRouteId && (
            <button
              onClick={() => setSelectedRouteId(null)}
              className="w-full mt-6 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 rounded-lg border border-slate-700 transition-colors"
            >
              Reset to System View
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default RouteMap;
