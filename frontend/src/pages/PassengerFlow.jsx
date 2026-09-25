// ─── PassengerFlow.jsx ────────────────────────────────────────────────────────
// Dashboard: Passenger Flow Analysis
// Shows: Passenger Type Distribution, Monthly Registrations, Boarding/Alighting
import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ScatterChart, Scatter, ZAxis
} from 'recharts';
import axios from 'axios';

// Color palette consistent across all charts
const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#3b82f6', '#8b5cf6'];

// Reusable card wrapper
const ChartCard = ({ title, children, className = '' }) => (
  <div className={`bg-white rounded-xl shadow-sm border border-gray-100 p-5 ${className}`}>
    <h3 className="text-base font-semibold text-gray-700 mb-4">{title}</h3>
    {children}
  </div>
);

export default function PassengerFlow() {
  const [flowData, setFlowData] = useState(null);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    axios.get('http://localhost:8000/analytics/passenger-flow')
      .then(res => { setFlowData(res.data); setLoading(false); })
      .catch(() => { setLoading(false); });
  }, []);

  // Fallback mock data while backend loads
  const passengerTypes = flowData?.passenger_types ?? [
    { name: 'Regular',  value: 32500 },
    { name: 'Student',  value: 11200 },
    { name: 'Senior',   value: 4800  },
    { name: 'Monthly',  value: 8700  },
  ];

  const monthlyReg = flowData?.monthly_registrations ?? [
    { month: 'Jan', registrations: 3200 },
    { month: 'Feb', registrations: 2800 },
    { month: 'Mar', registrations: 4100 },
    { month: 'Apr', registrations: 3700 },
    { month: 'May', registrations: 4500 },
    { month: 'Jun', registrations: 5200 },
    { month: 'Jul', registrations: 4900 },
    { month: 'Aug', registrations: 5600 },
    { month: 'Sep', registrations: 4300 },
    { month: 'Oct', registrations: 3900 },
    { month: 'Nov', registrations: 3400 },
    { month: 'Dec', registrations: 2900 },
  ];

  const hourlyTickets = flowData?.hourly_tickets ?? [
    { hour: '06', tickets: 1200 }, { hour: '07', tickets: 3400 },
    { hour: '08', tickets: 6800 }, { hour: '09', tickets: 4200 },
    { hour: '10', tickets: 2100 }, { hour: '11', tickets: 1800 },
    { hour: '12', tickets: 2400 }, { hour: '13', tickets: 2200 },
    { hour: '14', tickets: 1900 }, { hour: '15', tickets: 2600 },
    { hour: '16', tickets: 3800 }, { hour: '17', tickets: 7200 },
    { hour: '18', tickets: 5400 }, { hour: '19', tickets: 3100 },
    { hour: '20', tickets: 1600 }, { hour: '21', tickets: 900  },
  ];

  const weekdayVolume = flowData?.weekday_volume ?? [
    { day: 'Mon', trips: 4200 }, { day: 'Tue', trips: 4050 },
    { day: 'Wed', trips: 4300 }, { day: 'Thu', trips: 4150 },
    { day: 'Fri', trips: 4700 }, { day: 'Sat', trips: 3100 },
    { day: 'Sun', trips: 2400 },
  ];

  if (loading) return <p className="text-gray-500">Loading passenger flow data...</p>;

  const totalPassengers = passengerTypes.reduce((s, d) => s + d.value, 0);

  return (
    <div className="space-y-6 w-full">
      <h1 className="text-2xl font-bold text-gray-800">Passenger Flow Analysis</h1>

      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Passengers', value: totalPassengers.toLocaleString(), color: 'text-indigo-600' },
          { label: 'Peak Hour Tickets', value: '7,200', color: 'text-amber-600' },
          { label: 'Avg Daily Registrations', value: '410', color: 'text-emerald-600' },
          { label: 'Weekend Drop %', value: '37%', color: 'text-red-500' },
        ].map(k => (
          <div key={k.label} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <p className="text-xs text-gray-500">{k.label}</p>
            <p className={`text-2xl font-bold mt-1 ${k.color}`}>{k.value}</p>
          </div>
        ))}
      </div>

      {/* Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Passenger Type Distribution">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={passengerTypes} dataKey="value" nameKey="name"
                   cx="50%" cy="50%" outerRadius={90} innerRadius={50}
                   label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}>
                {passengerTypes.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(v) => v.toLocaleString()} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Monthly New Registrations Trend">
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={monthlyReg}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="registrations"
                    stroke="#6366f1" strokeWidth={2.5}
                    dot={{ r: 4 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Hourly Ticket Purchase Volume (Peak Detection)">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={hourlyTickets}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="hour" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="tickets" radius={[4, 4, 0, 0]}>
                {hourlyTickets.map((entry, i) => (
                  <Cell key={i}
                    fill={entry.tickets >= 5000 ? '#ef4444'
                        : entry.tickets >= 3000 ? '#f59e0b' : '#6366f1'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <p className="text-xs text-gray-400 mt-2">
            🔴 Peak ≥5000 &nbsp; 🟡 High 3000–5000 &nbsp; 🔵 Normal
          </p>
        </ChartCard>

        <ChartCard title="Trip Volume by Day of Week">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={weekdayVolume}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="day" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="trips" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}
