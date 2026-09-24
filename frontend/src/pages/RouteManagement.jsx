import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Route, Plus, Search, Map } from 'lucide-react';

const RouteManagement = () => {
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    const fetchRoutes = async () => {
      try {
        const res = await fetch('/api/admin/routes', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Failed to fetch routes');
        const data = await res.json();
        setRoutes(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchRoutes();
  }, [token]);

  if (loading) return <div className="text-slate-400">Loading routes...</div>;
  if (error) return <div className="text-red-400 p-4 bg-red-900/20 rounded-lg">{error}</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Route className="w-8 h-8 text-cyan-400" />
            Route Management
          </h1>
          <p className="text-slate-400 mt-1">Manage and configure transit routes.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors shadow-lg shadow-cyan-900/50">
          <Plus className="w-4 h-4" />
          Add Route
        </button>
      </div>

      <div className="bg-slate-800 rounded-xl border border-slate-700/50 overflow-hidden">
        <div className="p-4 border-b border-slate-700/50 flex items-center justify-between bg-slate-800/80">
          <div className="relative w-64">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search routes..." 
              className="w-full bg-slate-900/50 border border-slate-700 text-sm text-slate-200 rounded-lg pl-9 pr-3 py-2 focus:outline-none focus:border-cyan-500"
            />
          </div>
          <div className="text-sm text-slate-400 font-medium">
            Total Routes: {routes.length}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/50 text-slate-400 text-sm uppercase tracking-wider border-b border-slate-700">
                <th className="px-6 py-4 font-medium">ID</th>
                <th className="px-6 py-4 font-medium">Route Name</th>
                <th className="px-6 py-4 font-medium">Mode</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {routes.map((r) => (
                <tr key={r.id} className="hover:bg-slate-700/20 transition-colors text-sm">
                  <td className="px-6 py-4 font-mono text-cyan-400">{r.route_id}</td>
                  <td className="px-6 py-4 font-medium text-slate-200">{r.route_name}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 bg-slate-700/50 text-slate-300 rounded text-xs">
                      {r.transport_mode}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${r.active ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                      {r.active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-cyan-400 hover:text-cyan-300 font-medium text-sm">Edit</button>
                  </td>
                </tr>
              ))}
              {routes.length === 0 && (
                <tr>
                  <td colSpan="5" className="px-6 py-8 text-center text-slate-500">
                    No routes found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default RouteManagement;
