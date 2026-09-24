import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import SearchFilterBar from '../components/SearchFilterBar';
import { getDelays } from '../api/client';
import { Clock, AlertTriangle, ShieldAlert } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const SEVERITY_COLORS = ['#10b981', '#f59e0b', '#f97316', '#ef4444', '#7f1d1d'];

const DelayDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});

  useEffect(() => {
    setLoading(true);
    getDelays()
      .then(res => setData(res.data))
      .catch(err => {
        console.error("Delays API not ready:", err);
        setData(null);
      })
      .finally(() => setLoading(false));
  }, [filters]);

  return (
    <div>
      <Header
        title="Delay & Reliability Dashboard"
        subtitle="Network delay hotspots, severity breakdowns, and predicted risks"
      />
      
      <SearchFilterBar onFilterChange={setFilters} />

      {loading ? (
        <div className="p-8 text-center text-slate-400 glass-card">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full mb-2"></div>
          <p>Loading delay analytics from pipeline...</p>
        </div>
      ) : !data || !data.route_delays || data.route_delays.length === 0 ? (
        <div className="p-12 text-center text-slate-400 glass-card flex flex-col items-center">
          <Clock className="w-12 h-12 mb-4 text-slate-500" />
          <h3 className="text-lg font-bold text-white mb-2">No data available yet</h3>
          <p>Run the PySpark analytics pipeline to compute Delay data.</p>
        </div>
      ) : (
        <>
          {/* Row 1: Route-wise bar chart and Severity Pie Chart */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <div className="lg:col-span-2 glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">Route-Wise Avg Delay (Minutes)</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.route_delays}>
                    <XAxis dataKey="route_id" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                    <Bar dataKey="avg_delay" fill="#f59e0b" name="Avg Delay (min)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">Severity Breakdown</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data.severity_breakdown}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                      nameKey="name"
                    >
                      {data.severity_breakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={SEVERITY_COLORS[index % SEVERITY_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Row 2: Delay Trend and Bottlenecks */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">Delay Trend Over Time</h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data.delay_trend}>
                    <XAxis dataKey="date" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                    <Line type="monotone" dataKey="total_delay" stroke="#ef4444" strokeWidth={3} name="Total Delay (min)" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">Top Bottleneck Stops</h3>
              <div className="overflow-x-auto h-72">
                <table className="w-full text-left text-sm text-slate-300">
                  <thead className="text-xs uppercase bg-slate-800/80 text-slate-400">
                    <tr>
                      <th className="px-4 py-2">Stop ID</th>
                      <th className="px-4 py-2">Stop Name</th>
                      <th className="px-4 py-2 text-right">Avg Delay (min)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.bottlenecks.map((b, idx) => (
                      <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-800/30">
                        <td className="px-4 py-2 font-bold">{b.stop_id}</td>
                        <td className="px-4 py-2">{b.stop_name}</td>
                        <td className="px-4 py-2 text-right text-red-400 font-bold">{b.avg_delay}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Row 3: Model-Derived Risk Panel */}
          <div className="glass-card p-6 border-orange-500/30 bg-gradient-to-r from-slate-900 to-orange-950/20">
            <div className="flex items-center gap-3 mb-4">
              <ShieldAlert className="w-6 h-6 text-orange-400" />
              <h3 className="text-lg font-bold text-white">Predicted Delay Risk (Model-Derived)</h3>
            </div>
            <p className="text-sm text-slate-400 mb-4">
              These predictions are model-derived based on historical weather, traffic, and ridership patterns for upcoming trips in the next 2 hours.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {data.predicted_risks && data.predicted_risks.map((risk, idx) => (
                <div key={idx} className="bg-slate-800/80 p-4 rounded-lg border border-slate-700">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-bold text-cyan-400">{risk.route_id} - {risk.trip_id}</span>
                    <span className={`text-xs font-bold px-2 py-1 rounded ${
                      risk.risk_level === 'High' ? 'bg-red-900/50 text-red-400' : 'bg-orange-900/50 text-orange-400'
                    }`}>
                      {risk.risk_level} Risk
                    </span>
                  </div>
                  <p className="text-sm text-slate-300">Expected Delay: <span className="font-bold">{risk.expected_delay_min} min</span></p>
                  <p className="text-xs text-slate-400 mt-2">Primary Factor: {risk.primary_factor}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DelayDashboard;
