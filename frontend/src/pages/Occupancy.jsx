import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function Occupancy() {
  const data = [
    { time: '06:00', occ: 30 },
    { time: '08:00', occ: 95 },
    { time: '10:00', occ: 60 },
    { time: '12:00', occ: 55 },
    { time: '15:00', occ: 70 },
    { time: '17:30', occ: 105 },
    { time: '20:00', occ: 40 },
  ];

  return (
    <div className="space-y-6 w-full max-w-full">
      <h1 className="text-2xl font-bold text-gray-800">Occupancy & Crowding Risk</h1>
      
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Daily Occupancy Trend (Peak Hours)</h2>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="occ" stroke="#8b5cf6" fill="#c4b5fd" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold text-red-600 mb-2">High Risk Trips (>80%)</h2>
          <ul className="space-y-3">
            <li className="flex justify-between items-center bg-red-50 p-3 rounded">
              <span className="font-medium">R12 - 08:00 AM</span>
              <span className="text-red-700 font-bold">95%</span>
            </li>
            <li className="flex justify-between items-center bg-red-50 p-3 rounded">
              <span className="font-medium">R12 - 05:30 PM</span>
              <span className="text-red-700 font-bold">105% (Overcrowded)</span>
            </li>
          </ul>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold text-blue-600 mb-2">Underutilized Routes</h2>
          <ul className="space-y-3">
            <li className="flex justify-between items-center bg-blue-50 p-3 rounded">
              <span className="font-medium">R09 - All Day</span>
              <span className="text-blue-700 font-bold">22% Avg</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
