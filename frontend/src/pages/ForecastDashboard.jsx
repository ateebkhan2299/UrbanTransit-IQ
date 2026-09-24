import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import SearchFilterBar from '../components/SearchFilterBar';
import KpiCard from '../components/KpiCard';
import { getForecast } from '../api/client';
import { TrendingUp, AlertCircle, Target, Activity } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ForecastDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});

  useEffect(() => {
    setLoading(true);
    getForecast()
      .then(res => setData(res.data))
      .catch(err => {
        console.error("Forecast API not ready:", err);
        setData(null);
      })
      .finally(() => setLoading(false));
  }, [filters]);

  return (
    <div>
      <Header
        title="Predictive Demand Forecasting"
        subtitle="Future passenger volume predictions and pipeline model comparisons"
      />
      
      <SearchFilterBar onFilterChange={setFilters} />

      {loading ? (
        <div className="p-8 text-center text-slate-400 glass-card">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full mb-2"></div>
          <p>Loading forecast data from models...</p>
        </div>
      ) : !data || !data.demand_series || data.demand_series.length === 0 ? (
        <div className="p-12 text-center text-slate-400 glass-card flex flex-col items-center">
          <TrendingUp className="w-12 h-12 mb-4 text-slate-500" />
          <h3 className="text-lg font-bold text-white mb-2">No data available yet</h3>
          <p>Run the PySpark/Python dual-pipeline models to compute Forecasts.</p>
        </div>
      ) : (
        <>
          {/* Error Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6">
            <KpiCard title="MAE (Mean Absolute Error)" value={data.metrics?.mae || '0.0'} unit="passengers" icon={Target} color="cyan" />
            <KpiCard title="RMSE (Root Mean Square Error)" value={data.metrics?.rmse || '0.0'} unit="passengers" icon={Activity} color="purple" />
            <KpiCard title="MAPE (Mean Absolute Pct Error)" value={`${data.metrics?.mape || '0'}%`} icon={AlertCircle} color="amber" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* Forecast vs Actual Chart */}
            <div className="lg:col-span-2 glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">Historical vs Forecast Demand</h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data.demand_series}>
                    <XAxis dataKey="date" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                    <Legend />
                    <Line type="monotone" dataKey="actual" name="Actual Demand" stroke="#06b6d4" strokeWidth={3} />
                    <Line type="monotone" dataKey="forecast" name="Predicted Demand" stroke="#f59e0b" strokeWidth={3} strokeDasharray="5 5" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* High Demand Callouts */}
            <div className="glass-card p-6 border-cyan-500/30 bg-gradient-to-br from-slate-900 to-cyan-950/20">
              <div className="flex items-center gap-3 mb-4">
                <AlertCircle className="w-5 h-5 text-cyan-400" />
                <h3 className="text-lg font-bold text-white">Future High-Demand Callouts</h3>
              </div>
              <p className="text-sm text-slate-400 mb-4">Dates flagged by the model for abnormal peak volumes.</p>
              <div className="space-y-3 h-48 overflow-y-auto pr-2">
                {data.high_demand_callouts && data.high_demand_callouts.map((callout, idx) => (
                  <div key={idx} className="bg-slate-800/80 p-3 rounded-lg border border-slate-700 flex justify-between items-center">
                    <div>
                      <div className="font-bold text-white text-sm">{callout.date}</div>
                      <div className="text-xs text-slate-400">{callout.reason}</div>
                    </div>
                    <div className="text-cyan-400 font-bold">{callout.predicted_volume}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Dual Pipeline Comparison */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-bold text-white mb-4">Dual Pipeline Comparison (Spark MLlib vs Python Scikit-Learn)</h3>
            <p className="text-sm text-slate-400 mb-4">Recent test cases comparing model inferences from both required pipelines.</p>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/80 text-xs uppercase text-slate-400">
                  <tr>
                    <th className="px-4 py-3 rounded-tl-lg">Trip / Route ID</th>
                    <th className="px-4 py-3">Actual Result</th>
                    <th className="px-4 py-3 text-cyan-400">Spark MLlib Result</th>
                    <th className="px-4 py-3 text-purple-400">Python Scikit Result</th>
                    <th className="px-4 py-3">Difference</th>
                    <th className="px-4 py-3 rounded-tr-lg">Match?</th>
                  </tr>
                </thead>
                <tbody>
                  {data.model_comparison && data.model_comparison.map((row, idx) => (
                    <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-800/30">
                      <td className="px-4 py-3 font-bold">{row.target_id}</td>
                      <td className="px-4 py-3 font-bold">{row.actual}</td>
                      <td className="px-4 py-3 text-cyan-400 font-bold">{row.spark_result}</td>
                      <td className="px-4 py-3 text-purple-400 font-bold">{row.python_result}</td>
                      <td className="px-4 py-3">{row.difference}</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs font-bold px-2 py-1 rounded border ${
                          row.match ? 'bg-emerald-900/50 text-emerald-400 border-emerald-800' : 'bg-red-900/50 text-red-400 border-red-800'
                        }`}>
                          {row.match ? 'MATCH' : 'MISMATCH'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ForecastDashboard;
