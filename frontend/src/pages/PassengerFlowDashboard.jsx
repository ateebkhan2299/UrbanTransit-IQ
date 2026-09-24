import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import SearchFilterBar from '../components/SearchFilterBar';
import KpiCard from '../components/KpiCard';
import { getPassengerFlow } from '../api/client';
import { Users, Navigation, Map } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, ReferenceArea } from 'recharts';

const PassengerFlowDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});

  useEffect(() => {
    setLoading(true);
    getPassengerFlow()
      .then(res => {
        setData(res.data);
      })
      .catch(err => {
        console.error("Passenger Flow API not ready:", err);
        // Fallback to empty state instead of faking data
        setData(null);
      })
      .finally(() => setLoading(false));
  }, [filters]);

  return (
    <div>
      <Header
        title="Passenger Flow Dashboard"
        subtitle="Origin-Destination matrices, boarding patterns, and demand heatmaps"
      />
      
      <SearchFilterBar onFilterChange={setFilters} />

      {loading ? (
        <div className="p-8 text-center text-slate-400 glass-card">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full mb-2"></div>
          <p>Loading flow data from analytics pipeline...</p>
        </div>
      ) : !data || !data.boarding_alighting || data.boarding_alighting.length === 0 ? (
        <div className="p-12 text-center text-slate-400 glass-card flex flex-col items-center">
          <Users className="w-12 h-12 mb-4 text-slate-500" />
          <h3 className="text-lg font-bold text-white mb-2">No data available yet</h3>
          <p>Run the PySpark analytics pipeline to compute Passenger Flow data.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">
            <KpiCard
              title="Total Route Demand"
              value={data.total_demand || 0}
              unit="passengers"
              icon={Navigation}
              color="cyan"
            />
            <KpiCard
              title="Busiest Origin Stop"
              value={data.busiest_stop_name || 'N/A'}
              icon={Map}
              color="emerald"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">Boarding vs Alighting (Hourly)</h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.boarding_alighting}>
                    <XAxis dataKey="time" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                    <Legend />
                    <Bar dataKey="boarding" fill="#06b6d4" name="Boarding" />
                    <Bar dataKey="alighting" fill="#8b5cf6" name="Alighting" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">Daily Flow Trend & Peak Periods</h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data.peak_periods}>
                    <XAxis dataKey="time" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                    {/* Shaded bands for peak periods */}
                    <ReferenceArea x1="07:00" x2="09:00" strokeOpacity={0.3} fill="#ef4444" fillOpacity={0.1} />
                    <ReferenceArea x1="16:00" x2="18:30" strokeOpacity={0.3} fill="#ef4444" fillOpacity={0.1} />
                    <Line type="monotone" dataKey="volume" stroke="#10b981" strokeWidth={3} name="Total Volume" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div className="glass-card p-6">
            <h3 className="text-lg font-bold text-white mb-4">Origin-Destination Matrix</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="text-xs uppercase bg-slate-800/80 text-slate-400">
                  <tr>
                    <th className="px-4 py-3 rounded-tl-lg">Origin Stop</th>
                    <th className="px-4 py-3">Destination Stop</th>
                    <th className="px-4 py-3">Passenger Count</th>
                    <th className="px-4 py-3">Route</th>
                    <th className="px-4 py-3 rounded-tr-lg">Day Type</th>
                  </tr>
                </thead>
                <tbody>
                  {data.od_matrix.map((row, idx) => (
                    <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-800/30">
                      <td className="px-4 py-3">{row.origin}</td>
                      <td className="px-4 py-3">{row.destination}</td>
                      <td className="px-4 py-3 font-bold text-cyan-400">{row.count}</td>
                      <td className="px-4 py-3">{row.route_id}</td>
                      <td className="px-4 py-3">{row.day_type}</td>
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

export default PassengerFlowDashboard;
