import React, { useEffect, useState } from 'react';
import Header from '../components/Header';
import { getOccupancyHourly, getTopRoutes } from '../api/client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const PassengerFlow = () => {
  const [selectedRouteId, setSelectedRouteId] = useState(null);
  const [hourlyData, setHourlyData] = useState([]);
  const [topRoutes, setTopRoutes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getOccupancyHourly(selectedRouteId),
      getTopRoutes(5)
    ])
      .then(([occRes, topRes]) => {
        setHourlyData(occRes.data);
        setTopRoutes(topRes.data);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [selectedRouteId]);

  const hourlyAggregated = Array.from({ length: 24 }, (_, hour) => {
    const records = hourlyData.filter((d) => d.hour_of_day === hour);
    const avgPass = records.reduce((acc, curr) => acc + curr.avg_passengers, 0);
    return {
      hour: `${String(hour).padStart(2, '0')}:00`,
      passengers: Math.round(avgPass * 5),
    };
  });

  return (
    <div>
      <Header
        title="Passenger Flow & Volume Analytics"
        subtitle="Hourly boarding trends, peak hour dynamics, and network volume"
        selectedRouteId={selectedRouteId}
        onSelectRoute={setSelectedRouteId}
      />

      {loading ? (
        <div className="p-8 text-center text-slate-400">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-sky-400 border-t-transparent rounded-full mb-2"></div>
          <p>Loading Passenger Flow analytics...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 glass-card p-6">
            <h3 className="text-lg font-bold text-white mb-4">
              {selectedRouteId ? `Route ${selectedRouteId}` : 'Network-wide'} Boarding Volume (24 Hours)
            </h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={hourlyAggregated}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="hour" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                  <Bar dataKey="passengers" fill="#38bdf8" radius={[4, 4, 0, 0]} name="Passengers Boarded" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-card p-6">
            <h3 className="text-lg font-bold text-white mb-4">Top Volume Routes</h3>
            <div className="space-y-4">
              {topRoutes.map((r, idx) => (
                <div key={r.route_id} className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 border border-slate-700/50">
                  <div>
                    <div className="font-bold text-white text-sm">#{idx + 1} {r.route_name}</div>
                    <div className="text-xs text-slate-400">Occupancy: {r.occupancy_pct}%</div>
                  </div>
                  <div className="text-right">
                    <div className="text-cyan-400 font-extrabold text-sm">{r.total_passengers?.toLocaleString()}</div>
                    <div className="text-[11px] text-slate-400">passengers</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PassengerFlow;
