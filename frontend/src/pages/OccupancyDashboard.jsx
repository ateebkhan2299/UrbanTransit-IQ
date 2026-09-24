import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import SearchFilterBar from '../components/SearchFilterBar';
import KpiCard from '../components/KpiCard';
import { getOccupancy } from '../api/client';
import { Users, AlertCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

const getOccupancyColor = (pct) => {
  if (pct < 70) return 'text-emerald-400 bg-emerald-950/80 border-emerald-800';
  if (pct <= 90) return 'text-amber-400 bg-amber-950/80 border-amber-800';
  return 'text-red-400 bg-red-950/80 border-red-800';
};

const OccupancyDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});

  useEffect(() => {
    setLoading(true);
    getOccupancy()
      .then(res => setData(res.data))
      .catch(err => {
        console.error("Occupancy API not ready:", err);
        setData(null);
      })
      .finally(() => setLoading(false));
  }, [filters]);

  return (
    <div>
      <Header
        title="Occupancy & Crowding Analytics"
        subtitle="Route utilization, overcrowding alerts, and passenger comfort metrics"
      />
      
      <SearchFilterBar onFilterChange={setFilters} />

      {loading ? (
        <div className="p-8 text-center text-slate-400 glass-card">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full mb-2"></div>
          <p>Loading occupancy data from analytics pipeline...</p>
        </div>
      ) : !data || !data.occupancy_trend || data.occupancy_trend.length === 0 ? (
        <div className="p-12 text-center text-slate-400 glass-card flex flex-col items-center">
          <Users className="w-12 h-12 mb-4 text-slate-500" />
          <h3 className="text-lg font-bold text-white mb-2">No data available yet</h3>
          <p>Run the PySpark analytics pipeline to compute Occupancy data.</p>
        </div>
      ) : (
        <>
          {/* Summary Card */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
            <KpiCard
              title="Avg Capacity Utilization"
              value={`${data.avg_utilization || 0}%`}
              change={`${data.utilization_change || 0}%`}
              changeType={data.utilization_change >= 0 ? "positive" : "negative"}
              icon={Users}
              color="purple"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* Occupancy Line Chart */}
            <div className="lg:col-span-2 glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">Historical Occupancy Trend</h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data.occupancy_trend}>
                    <XAxis dataKey="time" stroke="#64748b" />
                    <YAxis stroke="#64748b" domain={[0, 150]} />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                    <Legend />
                    <ReferenceLine y={100} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'top', value: '100% Capacity', fill: '#ef4444', fontSize: 12 }} />
                    <Line type="monotone" dataKey="occupancy_pct" name="Occupancy %" stroke="#8b5cf6" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Overcrowded Routes List */}
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">Most Crowded Routes</h3>
              <div className="space-y-3 h-72 overflow-y-auto pr-2">
                {data.overcrowded_routes.map((route, idx) => (
                  <div key={idx} className="flex justify-between items-center p-3 rounded-lg bg-slate-800/60 border border-slate-700">
                    <div>
                      <div className="font-bold text-white text-sm">{route.route_id}</div>
                      <div className="text-xs text-slate-400">{route.route_name}</div>
                    </div>
                    <div className={`px-3 py-1 rounded text-sm font-bold border ${getOccupancyColor(route.occupancy_pct)}`}>
                      {route.occupancy_pct}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* High Risk Trips Table */}
          <div className="glass-card p-6">
            <div className="flex items-center gap-2 mb-4">
              <AlertCircle className="w-5 h-5 text-red-400" />
              <h3 className="text-lg font-bold text-white">Trips Flagged for Crowding Risk (Model-Derived)</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/80 text-xs uppercase text-slate-400">
                  <tr>
                    <th className="px-4 py-3 rounded-tl-lg">Trip ID</th>
                    <th className="px-4 py-3">Route</th>
                    <th className="px-4 py-3">Scheduled Start</th>
                    <th className="px-4 py-3">Predicted Occupancy</th>
                    <th className="px-4 py-3 rounded-tr-lg">Action Recommendation</th>
                  </tr>
                </thead>
                <tbody>
                  {data.high_risk_trips && data.high_risk_trips.map((trip, idx) => (
                    <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-800/30">
                      <td className="px-4 py-3 font-bold text-cyan-400">{trip.trip_id}</td>
                      <td className="px-4 py-3">{trip.route_id}</td>
                      <td className="px-4 py-3">{trip.scheduled_start}</td>
                      <td className="px-4 py-3 text-red-400 font-bold">{trip.predicted_occupancy}%</td>
                      <td className="px-4 py-3 text-xs text-slate-400">{trip.recommendation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default OccupancyDashboard;
