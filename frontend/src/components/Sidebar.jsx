import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  Users,
  Route,
  Clock,
  PieChart,
  TrendingUp,
  MapPin,
  Sliders,
  GitCompare,
  Bus,
  ShieldAlert,
  Activity,
  LogOut,
  Map,
  Terminal,
  Download
} from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { path: '/', label: 'Executive Dashboard', icon: LayoutDashboard },
    { path: '/flow', label: 'Passenger Flow', icon: Users },
    { path: '/routes', label: 'Route Performance', icon: Route },
    { path: '/delays', label: 'Delay Analytics', icon: Clock },
    { path: '/occupancy', label: 'Occupancy Risk', icon: PieChart },
    { path: '/forecast', label: 'Demand Forecast', icon: TrendingUp },
    { path: '/map', label: 'Interactive Route Map', icon: MapPin },
    { path: '/whatif', label: 'What-If Simulator', icon: Sliders },
    { path: '/comparison', label: 'Model Comparison', icon: GitCompare },
    { path: '/reports', label: 'Reports & Export', icon: Download },
  ];

  const adminItems = [
    { path: '/admin/routes', label: 'Route Manager', icon: Map },
    { path: '/admin/stops', label: 'Stop Manager', icon: MapPin },
    { path: '/admin/vehicles', label: 'Vehicle Manager', icon: Bus },
    { path: '/admin/trips', label: 'Trip Manager', icon: Route },
    { path: '/admin/schedules', label: 'Schedule Manager', icon: Clock },
    { path: '/admin/spark', label: 'Spark Jobs', icon: Terminal },
    { path: '/audit', label: 'Audit Trail', icon: ShieldAlert },
    { path: '/health', label: 'System Health', icon: Activity },
  ];

  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="w-64 glass-nav h-screen p-4 flex flex-col justify-between fixed left-0 top-0 z-30">
      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
        <div className="flex items-center gap-3 px-3 py-4 mb-6 border-b border-slate-800">
          <div className="p-2 bg-gradient-to-tr from-cyan-500 to-blue-600 rounded-xl shadow-lg shadow-cyan-500/20">
            <Bus className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white tracking-wide">UrbanTransit IQ</h1>
            <p className="text-xs text-cyan-400 font-medium">Big Data & AI Analytics</p>
          </div>
        </div>

        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/10 text-cyan-400 border-l-4 border-cyan-400 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
          
          {(user?.role === 'Admin' || user?.role === 'Evaluator') && (
            <div className="pt-4 pb-1 mt-4 border-t border-slate-800">
              <p className="px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Administration</p>
              {adminItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                        isActive
                          ? 'bg-gradient-to-r from-red-500/20 to-orange-500/10 text-red-400 border-l-4 border-red-400 shadow-sm'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </div>
          )}
        </nav>
      </div>

      <div className="mt-auto">
        <div className="px-3 py-3 rounded-t-lg bg-slate-800/50 border-t border-x border-slate-700/50 flex flex-col gap-1">
          <p className="text-sm font-semibold text-slate-200 truncate">{user?.full_name}</p>
          <div className="flex items-center justify-between">
            <span className="text-xs px-2 py-0.5 bg-slate-700 rounded text-slate-300">{user?.role}</span>
            <button onClick={handleLogout} className="text-slate-400 hover:text-red-400 p-1" title="Logout">
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
        <div className="px-3 py-3 rounded-b-lg bg-slate-800 border-b border-x border-slate-700/50 text-xs text-slate-400">
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="font-semibold text-slate-200">Engine Connected</span>
          </div>
          <p>PySpark & Sklearn Active</p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
