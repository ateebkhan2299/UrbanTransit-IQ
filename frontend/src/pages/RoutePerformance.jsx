import React, { useEffect, useState } from 'react';
import Header from '../components/Header';
import { getRoutes } from '../api/client';
import { Award, Zap, AlertTriangle, ChevronRight } from 'lucide-react';

const RoutePerformance = () => {
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRoutes()
      .then((res) => setRoutes(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const getTierBadge = (tier) => {
    switch (tier) {
      case 'Tier A':
        return 'bg-emerald-950 text-emerald-400 border-emerald-800';
      case 'Tier B':
        return 'bg-cyan-950 text-cyan-400 border-cyan-800';
      case 'Tier C':
        return 'bg-amber-950 text-amber-400 border-amber-800';
      default:
        return 'bg-rose-950 text-rose-400 border-rose-800';
    }
  };

  if (loading) {
    return <div className="p-8 text-slate-400">Loading Route Performance rankings...</div>;
  }

  return (
    <div>
      <Header
        title="Route Performance & ML Clustering Leaderboard"
        subtitle="Weighted multi-criteria scoring & KMeans cluster classification"
      />

      <div className="glass-card p-6 mb-8 overflow-hidden">
        <h3 className="text-lg font-bold text-white mb-4">Route Performance Matrix</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-700 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-4">Route ID</th>
                <th className="py-3 px-4">Route Name</th>
                <th className="py-3 px-4">Mode</th>
                <th className="py-3 px-4">Performance Score</th>
                <th className="py-3 px-4">Performance Tier</th>
                <th className="py-3 px-4">ML Cluster</th>
                <th className="py-3 px-4">On-Time %</th>
                <th className="py-3 px-4">Avg Delay</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-sm">
              {routes.map((r) => (
                <tr key={r.route_id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3 px-4 font-mono font-bold text-cyan-400">{r.route_id}</td>
                  <td className="py-3 px-4 font-semibold text-white">{r.route_name}</td>
                  <td className="py-3 px-4 text-slate-300">{r.transport_mode}</td>
                  <td className="py-3 px-4 font-extrabold text-white">{r.performance_score}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold border ${getTierBadge(r.performance_tier)}`}>
                      {r.performance_tier}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-300">
                    <span className="px-2 py-0.5 rounded text-xs bg-slate-800 border border-slate-700">
                      {r.cluster_label || `Cluster ${r.cluster_id}`}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-emerald-400 font-semibold">{r.on_time_performance_pct}%</td>
                  <td className="py-3 px-4 text-amber-400 font-semibold">{r.avg_delay_minutes} m</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default RoutePerformance;
