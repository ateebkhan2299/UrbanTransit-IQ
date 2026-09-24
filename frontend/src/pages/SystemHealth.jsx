import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Activity, Database, Clock, Cpu } from 'lucide-react';

const SystemHealth = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { token } = useAuth();

  const fetchHealth = async () => {
    try {
      const res = await fetch('/api/health', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setHealthData(data);
      }
    } catch (err) {
      console.error("Failed to fetch health data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, [token]);

  if (loading && !healthData) {
    return <div className="text-slate-400">Loading system health...</div>;
  }

  const isHealthy = healthData?.status === 'healthy';

  const formatUptime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return `${h}h ${m}m ${s}s`;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">System Health</h1>
        <p className="text-slate-400 mt-1">Real-time status of UrbanTransit IQ infrastructure.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700/50 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-slate-400 font-medium">Global Status</h3>
            <div className={`p-2 rounded-lg ${isHealthy ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
              <Activity />
            </div>
          </div>
          <div className="flex items-end gap-2">
            <span className="text-3xl font-bold uppercase">{healthData?.status || 'UNKNOWN'}</span>
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700/50 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-slate-400 font-medium">Database</h3>
            <div className={`p-2 rounded-lg ${healthData?.database === 'connected' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'}`}>
              <Database />
            </div>
          </div>
          <div className="flex items-end gap-2">
            <span className="text-3xl font-bold uppercase">{healthData?.database || 'UNKNOWN'}</span>
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700/50 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-slate-400 font-medium">Uptime</h3>
            <div className="p-2 rounded-lg bg-purple-500/20 text-purple-400">
              <Clock />
            </div>
          </div>
          <div className="flex items-end gap-2">
            <span className="text-3xl font-bold">{healthData ? formatUptime(healthData.uptime_seconds) : 'N/A'}</span>
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700/50 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-slate-400 font-medium">Memory Usage</h3>
            <div className="p-2 rounded-lg bg-orange-500/20 text-orange-400">
              <Cpu />
            </div>
          </div>
          <div className="flex items-end gap-2">
            <span className="text-3xl font-bold">{healthData?.memory_usage_mb || 0}</span>
            <span className="text-slate-400 mb-1">MB</span>
          </div>
        </div>
      </div>

      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700/50">
        <h3 className="text-lg font-medium mb-4">Last Check</h3>
        <p className="text-slate-300 font-mono text-sm">
          {healthData?.timestamp ? new Date(healthData.timestamp).toLocaleString() : 'N/A'}
        </p>
      </div>
    </div>
  );
};

export default SystemHealth;
