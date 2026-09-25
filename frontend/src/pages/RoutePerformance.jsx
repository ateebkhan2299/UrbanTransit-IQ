// ─── RoutePerformance.jsx ─────────────────────────────────────────────────────
// Dashboard: Route Performance Scoring & Classification
// Shows: Stops per route, Route Classification, Top/Bottom performers
import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, Cell
} from 'recharts';
import axios from 'axios';

const COLORS = ['#10b981', '#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6'];

const ChartCard = ({ title, children, className = '' }) => (
  <div className={`bg-white rounded-xl shadow-sm border border-gray-100 p-5 ${className}`}>
    <h3 className="text-base font-semibold text-gray-700 mb-4">{title}</h3>
    {children}
  </div>
);

const ClassBadge = ({ cls }) => {
  const map = {
    'High Performing' : 'bg-green-100 text-green-700',
    'Overcrowded'     : 'bg-red-100 text-red-700',
    'Low Performing'  : 'bg-yellow-100 text-yellow-700',
    'Balanced'        : 'bg-blue-100 text-blue-700',
    'Underutilized'   : 'bg-gray-100 text-gray-600',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${map[cls] ?? 'bg-gray-100 text-gray-600'}`}>
      {cls}
    </span>
  );
};

export default function RoutePerformance() {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://localhost:8000/analytics/route-performance')
      .then(res => { setData(res.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const topRoutes = data?.top_routes ?? [
    { route: 'R12', score: 91, on_time: 94, occupancy: 88, freq: 85 },
    { route: 'R04', score: 87, on_time: 89, occupancy: 72, freq: 90 },
    { route: 'R22', score: 83, on_time: 85, occupancy: 79, freq: 84 },
    { route: 'R08', score: 80, on_time: 82, occupancy: 65, freq: 88 },
    { route: 'R01', score: 76, on_time: 77, occupancy: 58, freq: 79 },
  ];

  const classificationData = data?.classification ?? [
    { name: 'High Performing', count: 28 },
    { name: 'Overcrowded',     count: 14 },
    { name: 'Balanced',        count: 32 },
    { name: 'Low Performing',  count: 18 },
    { name: 'Underutilized',   count: 13 },
  ];

  const radarData = data?.radar ?? [
    { metric: 'On-Time %',    R12: 94, R04: 89, R08: 82 },
    { metric: 'Occupancy',    R12: 88, R04: 72, R08: 65 },
    { metric: 'Frequency',    R12: 85, R04: 90, R08: 88 },
    { metric: 'Punctuality',  R12: 90, R04: 86, R08: 80 },
    { metric: 'Load Factor',  R12: 82, R04: 74, R08: 70 },
  ];

  const routeTable = data?.route_table ?? [
    { route: 'R12', classification: 'High Performing', score: 91, delay_avg: 5.2,  occ: 88 },
    { route: 'R04', classification: 'Overcrowded',     score: 87, delay_avg: 9.1,  occ: 105 },
    { route: 'R22', classification: 'Balanced',        score: 83, delay_avg: 7.4,  occ: 72 },
    { route: 'R09', classification: 'Underutilized',   score: 41, delay_avg: 3.1,  occ: 22 },
    { route: 'R17', classification: 'Low Performing',  score: 38, delay_avg: 21.5, occ: 34 },
  ];

  if (loading) return <p className="text-gray-500">Loading route performance data...</p>;

  return (
    <div className="space-y-6 w-full">
      <h1 className="text-2xl font-bold text-gray-800">Route Performance & Classification</h1>

      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Routes',        value: classificationData.reduce((s,d)=>s+d.count,0), color: 'text-indigo-600' },
          { label: 'High Performing',     value: classificationData.find(d=>d.name==='High Performing')?.count ?? 0, color: 'text-emerald-600' },
          { label: 'Overcrowded Routes',  value: classificationData.find(d=>d.name==='Overcrowded')?.count ?? 0, color: 'text-red-500' },
          { label: 'Underutilized',       value: classificationData.find(d=>d.name==='Underutilized')?.count ?? 0, color: 'text-amber-500' },
        ].map(k => (
          <div key={k.label} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <p className="text-xs text-gray-500">{k.label}</p>
            <p className={`text-2xl font-bold mt-1 ${k.color}`}>{k.value}</p>
          </div>
        ))}
      </div>

      {/* Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Route Classification Breakdown">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={classificationData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {classificationData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Top 5 Routes — Composite Performance Score">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={topRoutes}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="route" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="score" fill="#6366f1" radius={[4, 4, 0, 0]}
                   label={{ position: 'top', fontSize: 10 }} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Multi-Metric Radar — Top 3 Routes">
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 9 }} />
              <Radar name="R12" dataKey="R12" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} />
              <Radar name="R04" dataKey="R04" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
              <Radar name="R08" dataKey="R08" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.3} />
              <Legend />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Route Performance Table">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
                <tr>
                  <th className="p-2 text-left">Route</th>
                  <th className="p-2 text-left">Classification</th>
                  <th className="p-2 text-center">Score</th>
                  <th className="p-2 text-center">Avg Delay</th>
                  <th className="p-2 text-center">Occ %</th>
                </tr>
              </thead>
              <tbody>
                {routeTable.map(r => (
                  <tr key={r.route} className="border-b hover:bg-gray-50">
                    <td className="p-2 font-bold text-gray-700">{r.route}</td>
                    <td className="p-2"><ClassBadge cls={r.classification} /></td>
                    <td className="p-2 text-center font-semibold">{r.score}</td>
                    <td className="p-2 text-center text-red-500">{r.delay_avg} min</td>
                    <td className="p-2 text-center"
                        style={{ color: r.occ > 100 ? '#ef4444' : r.occ > 80 ? '#f59e0b' : '#10b981' }}>
                      {r.occ}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </ChartCard>
      </div>
    </div>
  );
}
