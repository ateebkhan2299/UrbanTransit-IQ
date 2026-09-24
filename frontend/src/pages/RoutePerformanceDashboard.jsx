import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import SearchFilterBar from '../components/SearchFilterBar';
import { getRoutePerformance } from '../api/client';
import { Activity, ChevronDown, ChevronUp } from 'lucide-react';
import { LineChart, Line, ResponsiveContainer, YAxis } from 'recharts';

const getCategoryColor = (category) => {
  switch (category) {
    case 'High Performing': return 'bg-emerald-950/80 text-emerald-400 border-emerald-800';
    case 'Overcrowded': return 'bg-rose-950/80 text-rose-400 border-rose-800';
    case 'Low Performing': return 'bg-red-950/80 text-red-400 border-red-800';
    case 'Reliable-but-Underutilized': return 'bg-amber-950/80 text-amber-400 border-amber-800';
    case 'High-Demand-but-Unreliable': return 'bg-orange-950/80 text-orange-400 border-orange-800';
    default: return 'bg-slate-800 text-slate-400 border-slate-700';
  }
};

const RoutePerformanceDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [expandedRoute, setExpandedRoute] = useState(null);
  
  // For sorting
  const [sortConfig, setSortConfig] = useState({ key: 'performance_score', direction: 'desc' });

  useEffect(() => {
    setLoading(true);
    getRoutePerformance()
      .then(res => setData(res.data))
      .catch(err => {
        console.error("Route Performance API not ready:", err);
        setData(null);
      })
      .finally(() => setLoading(false));
  }, [filters]);

  const handleSort = (key) => {
    let direction = 'desc';
    if (sortConfig.key === key && sortConfig.direction === 'desc') {
      direction = 'asc';
    }
    setSortConfig({ key, direction });
  };

  const sortedData = React.useMemo(() => {
    if (!data || !data.routes) return [];
    let sortableItems = [...data.routes];
    sortableItems.sort((a, b) => {
      if (a[sortConfig.key] < b[sortConfig.key]) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (a[sortConfig.key] > b[sortConfig.key]) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
    return sortableItems;
  }, [data, sortConfig]);

  return (
    <div>
      <Header
        title="Route Performance Dashboard"
        subtitle="Ranked evaluation of all transit routes and operational health"
      />
      
      <SearchFilterBar onFilterChange={setFilters} />

      {loading ? (
        <div className="p-8 text-center text-slate-400 glass-card">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full mb-2"></div>
          <p>Loading route performance data from analytics pipeline...</p>
        </div>
      ) : !data || !data.routes || data.routes.length === 0 ? (
        <div className="p-12 text-center text-slate-400 glass-card flex flex-col items-center">
          <Activity className="w-12 h-12 mb-4 text-slate-500" />
          <h3 className="text-lg font-bold text-white mb-2">No data available yet</h3>
          <p>Run the PySpark analytics pipeline to compute Route Performance data.</p>
        </div>
      ) : (
        <div className="glass-card p-6">
          <h3 className="text-lg font-bold text-white mb-4">Route Performance Rankings</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs uppercase bg-slate-800/80 text-slate-400">
                <tr>
                  <th className="px-4 py-3 rounded-tl-lg cursor-pointer" onClick={() => handleSort('route_id')}>Route ID</th>
                  <th className="px-4 py-3 cursor-pointer" onClick={() => handleSort('performance_score')}>Score</th>
                  <th className="px-4 py-3 cursor-pointer" onClick={() => handleSort('avg_delay')}>Avg Delay (min)</th>
                  <th className="px-4 py-3 cursor-pointer" onClick={() => handleSort('occupancy_pct')}>Occupancy %</th>
                  <th className="px-4 py-3 cursor-pointer" onClick={() => handleSort('reliability_pct')}>Reliability %</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3 rounded-tr-lg"></th>
                </tr>
              </thead>
              <tbody>
                {sortedData.map((row) => (
                  <React.Fragment key={row.route_id}>
                    <tr 
                      className={`border-b border-slate-700/50 hover:bg-slate-800/30 cursor-pointer ${expandedRoute === row.route_id ? 'bg-slate-800/40' : ''}`}
                      onClick={() => setExpandedRoute(expandedRoute === row.route_id ? null : row.route_id)}
                    >
                      <td className="px-4 py-3 font-bold text-cyan-400">{row.route_id}</td>
                      <td className="px-4 py-3 font-bold">{row.performance_score}</td>
                      <td className="px-4 py-3">{row.avg_delay}</td>
                      <td className="px-4 py-3">{row.occupancy_pct}%</td>
                      <td className="px-4 py-3">{row.reliability_pct}%</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs font-bold px-2 py-1 rounded border ${getCategoryColor(row.category)}`}>
                          {row.category}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        {expandedRoute === row.route_id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      </td>
                    </tr>
                    
                    {/* Expanded Drawer */}
                    {expandedRoute === row.route_id && (
                      <tr className="bg-slate-900/50 border-b border-slate-700/50">
                        <td colSpan="7" className="p-4">
                          <div className="flex gap-8">
                            <div className="flex-1">
                              <h4 className="text-xs text-slate-400 font-bold mb-2 uppercase">Delay Trend (Last 7 Days)</h4>
                              <div className="h-24 w-full bg-slate-800/50 rounded p-2">
                                <ResponsiveContainer width="100%" height="100%">
                                  <LineChart data={row.delay_trend || []}>
                                    <YAxis hide domain={['dataMin', 'dataMax']} />
                                    <Line type="monotone" dataKey="value" stroke="#ef4444" strokeWidth={2} dot={false} />
                                  </LineChart>
                                </ResponsiveContainer>
                              </div>
                            </div>
                            <div className="flex-1">
                              <h4 className="text-xs text-slate-400 font-bold mb-2 uppercase">Occupancy Trend (Last 7 Days)</h4>
                              <div className="h-24 w-full bg-slate-800/50 rounded p-2">
                                <ResponsiveContainer width="100%" height="100%">
                                  <LineChart data={row.occupancy_trend || []}>
                                    <YAxis hide domain={[0, 100]} />
                                    <Line type="monotone" dataKey="value" stroke="#8b5cf6" strokeWidth={2} dot={false} />
                                  </LineChart>
                                </ResponsiveContainer>
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoutePerformanceDashboard;
