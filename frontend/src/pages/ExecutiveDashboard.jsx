import React, { useEffect, useState } from 'react';
import Header from '../components/Header';
import KpiCard from '../components/KpiCard';
import { getDashboardSummary, getTopRoutes, getRecommendations } from '../api/client';
import { Users, Clock, PieChart, Activity, Layers, ArrowUpRight } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const ExecutiveDashboard = () => {
  const [selectedRouteId, setSelectedRouteId] = useState(null);
  const [summary, setSummary] = useState(null);
  const [topRoutes, setTopRoutes] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getDashboardSummary(selectedRouteId),
      getTopRoutes(5),
      getRecommendations(selectedRouteId)
    ])
      .then(([sumRes, topRes, recRes]) => {
        setSummary(sumRes.data);
        setTopRoutes(topRes.data);
        setRecommendations(recRes.data);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [selectedRouteId]);

  const sampleTrendData = [
    { time: '06:00', passengers: 1200, delay: 4.2 },
    { time: '08:00', passengers: 4800, delay: 14.5 },
    { time: '10:00', passengers: 2900, delay: 8.1 },
    { time: '12:00', passengers: 2100, delay: 5.0 },
    { time: '14:00', passengers: 2400, delay: 6.2 },
    { time: '16:00', passengers: 3800, delay: 11.4 },
    { time: '18:00', passengers: 5200, delay: 18.2 },
    { time: '20:00', passengers: 2100, delay: 7.3 },
  ];

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-400">
        <div className="animate-spin inline-block w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full mb-2"></div>
        <p>Loading Executive Dashboard from Backend API...</p>
      </div>
    );
  }

  return (
    <div>
      <Header
        title="Executive Overview Dashboard"
        subtitle="Real-time public transit operations summary & Big Data analytics"
        selectedRouteId={selectedRouteId}
        onSelectRoute={setSelectedRouteId}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <KpiCard
          title="Total Passengers Today"
          value={summary?.total_passengers?.toLocaleString() || '0'}
          unit="passengers"
          change={`${summary?.total_passengers_change_pct > 0 ? '+' : ''}${summary?.total_passengers_change_pct}%`}
          changeType={summary?.total_passengers_change_pct >= 0 ? 'positive' : 'negative'}
          icon={Users}
          color="cyan"
        />
        <KpiCard
          title="Total Scheduled Trips"
          value={summary?.total_trips?.toLocaleString() || '0'}
          unit="trips"
          change={`${summary?.total_trips_change_pct > 0 ? '+' : ''}${summary?.total_trips_change_pct}%`}
          changeType="positive"
          icon={Layers}
          color="emerald"
        />
        <KpiCard
          title="On-Time Performance"
          value={`${summary?.on_time_pct || 85.0}%`}
          change={`${summary?.on_time_change_pct > 0 ? '+' : ''}${summary?.on_time_change_pct}%`}
          changeType="positive"
          icon={Activity}
          color="amber"
        />
        <KpiCard
          title="Overall Capacity Utilization"
          value={`${summary?.avg_occupancy_pct || 0}%`}
          change={`${summary?.avg_occupancy_change_pct}%`}
          changeType="negative"
          icon={PieChart}
          color="purple"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Top Volume Routes */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-bold text-white mb-4">Top Volume Routes (Ranked)</h3>
          <div className="space-y-3">
            {topRoutes.map((r, idx) => (
              <div key={r.route_id} className="flex items-center justify-between p-3 rounded-lg bg-slate-800/60 border border-slate-700/60">
                <div className="flex items-center gap-3">
                  <span className="font-extrabold text-xs text-cyan-400 bg-cyan-950/80 px-2 py-1 rounded border border-cyan-800">
                    #{idx + 1}
                  </span>
                  <div>
                    <div className="font-bold text-white text-sm">{r.route_name}</div>
                    <div className="text-xs text-slate-400">Occupancy: {r.occupancy_pct}%</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-cyan-400 font-extrabold text-sm">{r.total_passengers?.toLocaleString()}</div>
                  <div className="text-[10px] text-slate-400">passengers</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Hourly Volume Chart */}
        <div className="lg:col-span-2 glass-card p-6">
          <h3 className="text-lg font-bold text-white mb-4">System Hourly Passenger Volume Trend</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={sampleTrendData}>
                <defs>
                  <linearGradient id="passGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                <Area type="monotone" dataKey="passengers" stroke="#06b6d4" fillOpacity={1} fill="url(#passGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExecutiveDashboard;
