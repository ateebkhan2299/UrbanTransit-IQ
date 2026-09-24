import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

const AuditTrail = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    const fetchAuditLogs = async () => {
      try {
        const res = await fetch('/api/admin/audit-trail', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (!res.ok) {
          if (res.status === 403) {
            throw new Error("Access forbidden: Requires Admin or Evaluator role.");
          }
          throw new Error('Failed to fetch audit logs');
        }
        const data = await res.json();
        setLogs(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAuditLogs();
  }, [token]);

  if (loading) {
    return <div className="text-slate-400">Loading audit trail...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-6 rounded-xl">
        <h3 className="text-lg font-semibold mb-2">Access Denied</h3>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Security Audit Trail</h1>
        <p className="text-slate-400 mt-1">Review system access and critical actions.</p>
      </div>

      <div className="bg-slate-800 rounded-xl border border-slate-700/50 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/50 text-slate-400 text-sm uppercase tracking-wider border-b border-slate-700">
                <th className="px-6 py-4 font-medium">Timestamp</th>
                <th className="px-6 py-4 font-medium">User</th>
                <th className="px-6 py-4 font-medium">Role</th>
                <th className="px-6 py-4 font-medium">Action</th>
                <th className="px-6 py-4 font-medium">Endpoint</th>
                <th className="px-6 py-4 font-medium">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-700/20 transition-colors text-sm">
                  <td className="px-6 py-4 text-slate-300 whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 font-medium text-blue-400">
                    {log.username}
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 bg-slate-700 text-slate-300 rounded text-xs">
                      {log.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-300 font-mono">
                    {log.action}
                  </td>
                  <td className="px-6 py-4 text-slate-400">
                    {log.endpoint}
                  </td>
                  <td className="px-6 py-4 text-slate-400 truncate max-w-xs" title={log.details}>
                    {log.details || '-'}
                  </td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-slate-500">
                    No audit logs found.
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

export default AuditTrail;
