// ─── Forecast.jsx ─────────────────────────────────────────────────────────────
// Dashboard: Demand Forecasting & Occupancy Predictions
// Shows: 12-month forecast, ML model comparison, confidence bands
import React, { useState, useEffect } from 'react';
import {
  AreaChart, Area, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell, ReferenceLine
} from 'recharts';
import axios from 'axios';

const ChartCard = ({ title, subtitle, children, className = '' }) => (
  <div className={`bg-white rounded-xl shadow-sm border border-gray-100 p-5 ${className}`}>
    <h3 className="text-base font-semibold text-gray-700">{title}</h3>
    {subtitle && <p className="text-xs text-gray-400 mb-3">{subtitle}</p>}
    {!subtitle && <div className="mb-4" />}
    {children}
  </div>
);

export default function Forecast() {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://localhost:8000/analytics/forecast')
      .then(res => { setData(res.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  // 12-month demand forecast data
  const forecastData = data?.demand_forecast ?? [
    { month: 'Jan',  actual: 162000, spark_pred: null,   py_pred: null   },
    { month: 'Feb',  actual: 148000, spark_pred: null,   py_pred: null   },
    { month: 'Mar',  actual: 175000, spark_pred: null,   py_pred: null   },
    { month: 'Apr',  actual: 182000, spark_pred: null,   py_pred: null   },
    { month: 'May',  actual: 191000, spark_pred: null,   py_pred: null   },
    { month: 'Jun',  actual: 205000, spark_pred: null,   py_pred: null   },
    { month: 'Jul',  actual: 198000, spark_pred: null,   py_pred: null   },
    { month: 'Aug',  actual: 212000, spark_pred: null,   py_pred: null   },
    { month: 'Sep',  actual: 207000, spark_pred: 204000, py_pred: 209000 },
    { month: 'Oct',  actual: null,   spark_pred: 218000, py_pred: 221000 },
    { month: 'Nov',  actual: null,   spark_pred: 229000, py_pred: 226000 },
    { month: 'Dec',  actual: null,   spark_pred: 241000, py_pred: 238000 },
  ];

  // Model comparison metrics
  const modelMetrics = data?.model_metrics ?? [
    { model: 'Spark Linear',  MAE: 4200, RMSE: 5800, MAPE: 3.1 },
    { model: 'Spark RF',      MAE: 3100, RMSE: 4200, MAPE: 2.4 },
    { model: 'Spark GBT',     MAE: 2900, RMSE: 3900, MAPE: 2.1 },
    { model: 'Py Linear',     MAE: 4500, RMSE: 6100, MAPE: 3.4 },
    { model: 'Py XGBoost',    MAE: 2700, RMSE: 3600, MAPE: 1.9 },
    { model: 'Py Prophet',    MAE: 3300, RMSE: 4500, MAPE: 2.7 },
  ];

  // Occupancy risk trend
  const occupancyTrend = data?.occupancy_trend ?? [
    { time: '06:00', occ: 28  },
    { time: '07:00', occ: 55  },
    { time: '08:00', occ: 97  },
    { time: '09:00', occ: 78  },
    { time: '10:00', occ: 52  },
    { time: '11:00', occ: 44  },
    { time: '12:00', occ: 58  },
    { time: '13:00', occ: 55  },
    { time: '14:00', occ: 48  },
    { time: '15:00', occ: 62  },
    { time: '16:00', occ: 74  },
    { time: '17:00', occ: 105 },
    { time: '18:00', occ: 88  },
    { time: '19:00', occ: 62  },
    { time: '20:00', occ: 38  },
  ];

  if (loading) return <p className="text-gray-500">Loading forecast data...</p>;

  return (
    <div className="space-y-6 w-full">
      <h1 className="text-2xl font-bold text-gray-800">Demand Forecast & Occupancy Prediction</h1>

      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Dec Forecast (Spark)', value: '241,000',  color: 'text-indigo-600' },
          { label: 'Dec Forecast (Python)', value: '238,000', color: 'text-emerald-600' },
          { label: 'Best Model MAE',        value: '2,700',   color: 'text-blue-600'   },
          { label: 'Best Model MAPE',       value: '1.9%',    color: 'text-amber-500'  },
        ].map(k => (
          <div key={k.label} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <p className="text-xs text-gray-500">{k.label}</p>
            <p className={`text-2xl font-bold mt-1 ${k.color}`}>{k.value}</p>
          </div>
        ))}
      </div>

      {/* Forecast chart */}
      <ChartCard
        title="12-Month Passenger Demand Forecast"
        subtitle="Actual (solid) vs Spark Prediction (dashed purple) vs Python Prediction (dashed green)">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={forecastData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="month" tick={{ fontSize: 11 }} />
            <YAxis tickFormatter={v => `${(v/1000).toFixed(0)}K`} tick={{ fontSize: 11 }} />
            <Tooltip formatter={v => v ? v.toLocaleString() : 'N/A'} />
            <Legend />
            <ReferenceLine x="Sep" stroke="#94a3b8" strokeDasharray="4 4"
                           label={{ value: 'Forecast Start', position: 'top', fontSize: 10 }} />
            <Line type="monotone" dataKey="actual"     name="Actual"
                  stroke="#3b82f6" strokeWidth={2.5} dot={{ r: 4 }} connectNulls={false} />
            <Line type="monotone" dataKey="spark_pred" name="Spark Forecast"
                  stroke="#8b5cf6" strokeWidth={2} strokeDasharray="5 4"
                  dot={{ r: 3 }} connectNulls />
            <Line type="monotone" dataKey="py_pred"    name="Python Forecast"
                  stroke="#10b981" strokeWidth={2} strokeDasharray="5 4"
                  dot={{ r: 3 }} connectNulls />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Model MAE Comparison (Lower = Better)">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={modelMetrics} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" tick={{ fontSize: 10 }} />
              <YAxis dataKey="model" type="category" width={90} tick={{ fontSize: 10 }} />
              <Tooltip />
              <Bar dataKey="MAE" radius={[0, 4, 4, 0]}>
                {modelMetrics.map((entry, i) => (
                  <Cell key={i}
                    fill={entry.model.startsWith('Spark') ? '#8b5cf6' : '#10b981'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="flex gap-4 mt-2 text-xs text-gray-500">
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-violet-500 inline-block" /> Spark MLlib</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-emerald-500 inline-block" /> Python Pipeline</span>
          </div>
        </ChartCard>

        <ChartCard title="Hourly Occupancy Forecast (Today)">
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={occupancyTrend}>
              <defs>
                <linearGradient id="occGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0}   />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="time" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 120]} tick={{ fontSize: 11 }} />
              <Tooltip formatter={v => `${v}%`} />
              <ReferenceLine y={100} stroke="#ef4444" strokeDasharray="4 4"
                             label={{ value: 'Capacity 100%', position: 'right', fontSize: 10, fill: '#ef4444' }} />
              <ReferenceLine y={80} stroke="#f59e0b" strokeDasharray="4 4"
                             label={{ value: '80% Alert', position: 'right', fontSize: 10, fill: '#f59e0b' }} />
              <Area type="monotone" dataKey="occ" name="Occupancy %"
                    stroke="#6366f1" fill="url(#occGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}
