import React, { useEffect, useState } from 'react';
import Header from '../components/Header';
import { getModelComparison } from '../api/client';
import { GitCompare, Cpu, Database, CheckCircle } from 'lucide-react';

const ModelComparison = () => {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getModelComparison()
      .then((res) => setReport(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-slate-400">Loading Dual-Pipeline Model Comparison...</div>;
  }

  const models = report?.models || {};

  return (
    <div>
      <Header
        title="Dual-Pipeline Model Benchmarking & Comparison"
        subtitle="Independent evaluation of Big Data Apache Spark MLlib vs Python Scikit-Learn / XGBoost models"
      />

      <div className="glass-card p-6 mb-8">
        <div className="flex items-center gap-3 mb-6">
          <GitCompare className="w-6 h-6 text-cyan-400" />
          <h3 className="text-xl font-bold text-white">Pipeline Architectural Performance Matrix</h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-700 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-4">ML Task</th>
                <th className="py-3 px-4">Metric</th>
                <th className="py-3 px-4">
                  <div className="flex items-center gap-1.5 text-amber-400">
                    <Database className="w-4 h-4" />
                    <span>Spark MLlib (Big Data)</span>
                  </div>
                </th>
                <th className="py-3 px-4">
                  <div className="flex items-center gap-1.5 text-cyan-400">
                    <Cpu className="w-4 h-4" />
                    <span>Python Sklearn/XGBoost</span>
                  </div>
                </th>
                <th className="py-3 px-4">Pipeline Winner</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-sm">
              {/* Delay Prediction */}
              <tr className="hover:bg-slate-800/40">
                <td className="py-4 px-4 font-bold text-white">Delay Prediction</td>
                <td className="py-4 px-4 text-slate-400">R² Score / RMSE</td>
                <td className="py-4 px-4 font-mono text-slate-200">
                  R²={models?.delay_prediction?.spark_mllib?.r2?.toFixed(4) || 'N/A'}<br />
                  <span className="text-xs text-slate-400">RMSE={models?.delay_prediction?.spark_mllib?.rmse?.toFixed(2) || 'N/A'}</span>
                </td>
                <td className="py-4 px-4 font-mono text-slate-200">
                  R²={models?.delay_prediction?.python_sklearn?.r2?.toFixed(4) || 'N/A'}<br />
                  <span className="text-xs text-slate-400">RMSE={models?.delay_prediction?.python_sklearn?.rmse?.toFixed(2) || 'N/A'}</span>
                </td>
                <td className="py-4 px-4">
                  <span className="px-2.5 py-1 rounded text-xs font-bold bg-cyan-950 text-cyan-400 border border-cyan-800 uppercase">
                    {models?.delay_prediction?.winner || 'python_sklearn'}
                  </span>
                </td>
              </tr>

              {/* Demand Forecast */}
              <tr className="hover:bg-slate-800/40">
                <td className="py-4 px-4 font-bold text-white">Demand Forecast</td>
                <td className="py-4 px-4 text-slate-400">R² Score / MAE</td>
                <td className="py-4 px-4 font-mono text-slate-200">
                  R²={models?.demand_forecast?.spark_mllib?.r2?.toFixed(4) || 'N/A'}<br />
                  <span className="text-xs text-slate-400">MAE={models?.demand_forecast?.spark_mllib?.mae?.toFixed(1) || 'N/A'}</span>
                </td>
                <td className="py-4 px-4 font-mono text-slate-200">
                  R²={models?.demand_forecast?.python_sklearn?.r2?.toFixed(4) || 'N/A'}<br />
                  <span className="text-xs text-slate-400">MAE={models?.demand_forecast?.python_sklearn?.mae?.toFixed(1) || 'N/A'}</span>
                </td>
                <td className="py-4 px-4">
                  <span className="px-2.5 py-1 rounded text-xs font-bold bg-cyan-950 text-cyan-400 border border-cyan-800 uppercase">
                    {models?.demand_forecast?.winner || 'python_sklearn'}
                  </span>
                </td>
              </tr>

              {/* Occupancy Risk */}
              <tr className="hover:bg-slate-800/40">
                <td className="py-4 px-4 font-bold text-white">Occupancy Overcrowd Risk</td>
                <td className="py-4 px-4 text-slate-400">F1-Score / Accuracy</td>
                <td className="py-4 px-4 font-mono text-slate-200">
                  F1={models?.occupancy_risk?.spark_mllib?.f1?.toFixed(4) || 'N/A'}<br />
                  <span className="text-xs text-slate-400">Acc={models?.occupancy_risk?.spark_mllib?.accuracy?.toFixed(4) || 'N/A'}</span>
                </td>
                <td className="py-4 px-4 font-mono text-slate-200">
                  F1={models?.occupancy_risk?.python_sklearn?.f1?.toFixed(4) || 'N/A'}<br />
                  <span className="text-xs text-slate-400">Acc={models?.occupancy_risk?.python_sklearn?.accuracy?.toFixed(4) || 'N/A'}</span>
                </td>
                <td className="py-4 px-4">
                  <span className="px-2.5 py-1 rounded text-xs font-bold bg-cyan-950 text-cyan-400 border border-cyan-800 uppercase">
                    {models?.occupancy_risk?.winner || 'python_sklearn'}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ModelComparison;
