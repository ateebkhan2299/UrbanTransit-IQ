import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Play, CheckCircle, XCircle, Clock } from 'lucide-react';

const SparkJobs = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await fetch('/api/admin/spark-jobs', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Failed to fetch spark jobs status');
        const data = await res.json();
        setJobs(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchJobs();
    const interval = setInterval(fetchJobs, 15000);
    return () => clearInterval(interval);
  }, [token]);

  if (loading) return <div className="text-slate-400">Loading spark jobs...</div>;
  if (error) return <div className="text-red-400 p-4 bg-red-900/20 rounded-lg">{error}</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Play className="w-8 h-8 text-purple-400" />
            Spark Job Monitoring
          </h1>
          <p className="text-slate-400 mt-1">Real-time status of PySpark analytics pipelines.</p>
        </div>
        <button className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition-colors shadow-lg shadow-purple-900/50">
          Trigger Pipeline Run
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {jobs.map((job) => (
          <div key={job.id} className="bg-slate-800 rounded-xl border border-slate-700/50 p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="mt-1">
                {job.status === 'Success' && <CheckCircle className="w-6 h-6 text-emerald-400" />}
                {job.status === 'Failed' && <XCircle className="w-6 h-6 text-red-400" />}
                {job.status === 'Running' && <Clock className="w-6 h-6 text-amber-400 animate-pulse" />}
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-200">{job.job_name}.py</h3>
                <div className="flex flex-wrap gap-4 mt-2 text-sm text-slate-400">
                  <span>Started: {new Date(job.start_time).toLocaleString()}</span>
                  {job.end_time && <span>Finished: {new Date(job.end_time).toLocaleString()}</span>}
                  {job.duration_seconds && <span>Duration: {job.duration_seconds}s</span>}
                  {job.records_processed !== null && <span>Records: {job.records_processed.toLocaleString()}</span>}
                </div>
                {job.error_message && (
                  <div className="mt-3 p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-mono rounded">
                    {job.error_message}
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex-shrink-0">
              <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider
                ${job.status === 'Success' ? 'bg-emerald-500/20 text-emerald-400' : ''}
                ${job.status === 'Failed' ? 'bg-red-500/20 text-red-400' : ''}
                ${job.status === 'Running' ? 'bg-amber-500/20 text-amber-400' : ''}
              `}>
                {job.status}
              </span>
            </div>
          </div>
        ))}
        {jobs.length === 0 && (
          <div className="text-slate-500 p-8 text-center bg-slate-800 rounded-xl border border-slate-700/50">
            No pipeline executions recorded.
          </div>
        )}
      </div>
    </div>
  );
};

export default SparkJobs;
