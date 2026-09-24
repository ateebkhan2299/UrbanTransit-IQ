import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Lock, User, ArrowRight } from 'lucide-react';

const Login = () => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-slate-800 rounded-2xl shadow-xl overflow-hidden border border-slate-700/50">
        <div className="p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">
              UrbanTransit IQ
            </h1>
            <p className="text-slate-400 mt-2">Sign in to your account</p>
          </div>
          
          {error && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-3 rounded-lg mb-6 text-sm text-center">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Username</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <User size={18} />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2 border border-slate-600 rounded-lg bg-slate-900/50 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="Enter username"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <Lock size={18} />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2 border border-slate-600 rounded-lg bg-slate-900/50 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="Enter password"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  Sign In
                  <ArrowRight size={18} className="ml-2" />
                </>
              )}
            </button>
          </form>
          
          <div className="mt-8 border-t border-slate-700 pt-6">
            <p className="text-xs text-slate-500 text-center mb-2">Demo Roles:</p>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <button
                type="button"
                onClick={() => { setUsername('admin'); setPassword('AdminSecure2026!'); }}
                className="px-2 py-2 bg-slate-700/50 hover:bg-slate-700 rounded text-slate-300 transition-colors text-left"
              >
                <strong className="block text-white">admin</strong>
                <span className="text-[10px] text-slate-400">AdminSecure2026!</span>
              </button>
              <button
                type="button"
                onClick={() => { setUsername('operator'); setPassword('OperatorPass_99'); }}
                className="px-2 py-2 bg-slate-700/50 hover:bg-slate-700 rounded text-slate-300 transition-colors text-left"
              >
                <strong className="block text-white">operator</strong>
                <span className="text-[10px] text-slate-400">OperatorPass_99</span>
              </button>
              <button
                type="button"
                onClick={() => { setUsername('analyst'); setPassword('AnalystData#26'); }}
                className="px-2 py-2 bg-slate-700/50 hover:bg-slate-700 rounded text-slate-300 transition-colors text-left"
              >
                <strong className="block text-white">analyst</strong>
                <span className="text-[10px] text-slate-400">AnalystData#26</span>
              </button>
              <button
                type="button"
                onClick={() => { setUsername('evaluator'); setPassword('Evaluator_Audit_1'); }}
                className="px-2 py-2 bg-slate-700/50 hover:bg-slate-700 rounded text-slate-300 transition-colors text-left"
              >
                <strong className="block text-white">evaluator</strong>
                <span className="text-[10px] text-slate-400">Evaluator_Audit_1</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
