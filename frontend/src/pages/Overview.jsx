import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function Overview() {
  const data = [
    { period: 'Jan', passengers: 4000 },
    { period: 'Feb', passengers: 3000 },
    { period: 'Mar', passengers: 2000 },
    { period: 'Apr', passengers: 2780 },
    { period: 'May', passengers: 1890 },
    { period: 'Jun', passengers: 2390 },
    { period: 'Jul', passengers: 3490 },
  ];

  return (
    <div className="space-y-6 w-full max-w-full">
      <h1 className="text-2xl font-bold text-gray-800">Executive Overview</h1>
      
      {/* Responsive Grid for KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Total Passengers</p>
          <p className="text-2xl font-bold text-gray-800">2,150,000</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">On-Time %</p>
          <p className="text-2xl font-bold text-green-600">82.4%</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Avg Occupancy</p>
          <p className="text-2xl font-bold text-blue-600">65.2%</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Active Anomalies</p>
          <p className="text-2xl font-bold text-red-600">12</p>
        </div>
      </div>

      {/* Responsive Chart Container */}
      <div className="bg-white p-4 md:p-6 rounded-lg shadow-sm border border-gray-100 w-full overflow-hidden">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Passenger Trend</h2>
        <div className="h-64 sm:h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid stroke="#f5f5f5" />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="passengers" stroke="#2563eb" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
