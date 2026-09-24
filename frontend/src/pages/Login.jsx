import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Hardcoded mock for demo skeleton
    login({ username: username || 'admin', role: 'Administrator' });
    navigate('/overview');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-md max-w-md w-full p-6 sm:p-8">
        <h1 className="text-2xl font-bold text-center text-blue-600 mb-6">UrbanTransit IQ</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input 
              className="w-full border rounded-md p-2 focus:ring-blue-500 focus:border-blue-500" 
              value={username} 
              onChange={e => setUsername(e.target.value)} 
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input 
              type="password" 
              className="w-full border rounded-md p-2 focus:ring-blue-500 focus:border-blue-500" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
            />
          </div>
          <button type="submit" className="w-full bg-blue-600 text-white rounded-md py-2 font-medium hover:bg-blue-700 transition-colors">
            Login
          </button>
        </form>
        <div className="mt-4 text-xs text-gray-500 text-center">
          <p>Demo accounts: admin, operator, analyst, evaluator</p>
        </div>
      </div>
    </div>
  );
}
