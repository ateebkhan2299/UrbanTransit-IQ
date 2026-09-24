import React from 'react';

export default function Admin() {
  const users = [
    { id: 1, username: 'admin', role: 'Administrator', status: 'Active' },
    { id: 2, username: 'operator', role: 'Operator', status: 'Active' },
    { id: 3, username: 'analyst', role: 'Analyst', status: 'Active' },
    { id: 4, username: 'evaluator', role: 'Evaluator', status: 'Active' },
  ];

  return (
    <div className="space-y-6 w-full max-w-full">
      <h1 className="text-2xl font-bold text-gray-800">Admin Control Panel</h1>
      
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-700">User Management</h2>
          <button className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 transition">
            + Create User
          </button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-100 text-gray-600">
              <tr>
                <th className="p-3">ID</th>
                <th className="p-3">Username</th>
                <th className="p-3">Role</th>
                <th className="p-3">Status</th>
                <th className="p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} className="border-b hover:bg-gray-50">
                  <td className="p-3">{u.id}</td>
                  <td className="p-3 font-medium">{u.username}</td>
                  <td className="p-3">
                    <span className="bg-gray-200 text-gray-800 px-2 py-1 rounded text-xs">{u.role}</span>
                  </td>
                  <td className="p-3 text-green-600">{u.status}</td>
                  <td className="p-3">
                    <button className="text-blue-600 hover:underline mr-3">Edit</button>
                    <button className="text-red-600 hover:underline">Deactivate</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Audit Log (Read Only)</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-gray-500">
            <thead className="bg-gray-50">
              <tr>
                <th className="p-2">Timestamp</th>
                <th className="p-2">User</th>
                <th className="p-2">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b">
                <td className="p-2">2026-09-24 10:00:00</td>
                <td className="p-2">admin</td>
                <td className="p-2">Created user 'evaluator'</td>
              </tr>
              <tr>
                <td className="p-2">2026-09-24 10:05:00</td>
                <td className="p-2">operator</td>
                <td className="p-2">Marked REC-0001 as Acknowledged</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
