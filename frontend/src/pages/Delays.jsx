import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function Delays() {
  const data = [
    { route: 'R12', delay_min: 15 },
    { route: 'R04', delay_min: 22 },
    { route: 'R08', delay_min: 8 },
    { route: 'R22', delay_min: 12 },
    { route: 'R01', delay_min: 5 },
  ];

  return (
    <div className="space-y-6 w-full max-w-full">
      <h1 className="text-2xl font-bold text-gray-800">Delay Analysis & Prediction</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Average Delay by Route</h2>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="route" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="delay_min" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Dual-Pipeline Predictions</h2>
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 text-gray-600">
              <tr>
                <th className="p-2">Trip ID</th>
                <th className="p-2">Spark Model</th>
                <th className="p-2">Python Model</th>
                <th className="p-2">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b">
                <td className="p-2 font-medium">TR-8812</td>
                <td className="p-2 text-yellow-600">12 min</td>
                <td className="p-2 text-yellow-600">14 min</td>
                <td className="p-2"><span className="bg-green-100 text-green-700 px-2 py-1 rounded">Match</span></td>
              </tr>
              <tr className="border-b">
                <td className="p-2 font-medium">TR-4192</td>
                <td className="p-2 text-red-600">25 min</td>
                <td className="p-2 text-green-600">On Time</td>
                <td className="p-2"><span className="bg-red-100 text-red-700 px-2 py-1 rounded">Mismatch</span></td>
              </tr>
              <tr>
                <td className="p-2 font-medium">TR-1102</td>
                <td className="p-2 text-green-600">On Time</td>
                <td className="p-2 text-green-600">On Time</td>
                <td className="p-2"><span className="bg-green-100 text-green-700 px-2 py-1 rounded">Match</span></td>
              </tr>
            </tbody>
          </table>
          <p className="text-xs text-gray-500 mt-4">* Mismatch detected due to high variance in historical weather features.</p>
        </div>
      </div>
    </div>
  );
}
