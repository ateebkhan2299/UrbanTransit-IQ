import React, { useState } from 'react';
import { Outlet, Link, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { LayoutDashboard, Lightbulb, Map, Menu, X, LogOut } from 'lucide-react';

export default function Shell() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  // If not logged in, redirect
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const navItems = [
    { name: 'Overview', path: '/overview', icon: LayoutDashboard },
    { name: 'Recommendations', path: '/recommendations', icon: Lightbulb },
    { name: 'Route Map', path: '/map', icon: Map },
  ];

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Mobile Sidebar Overlay */}
      {mobileOpen && (
        <div 
          className="fixed inset-0 z-40 bg-gray-900 bg-opacity-50 md:hidden"
          onClick={() => setMobileOpen(false)}
        ></div>
      )}

      {/* Sidebar - responsive (hidden on mobile by default) */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r shadow-sm transform transition-transform duration-300 md:relative md:translate-x-0 ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="p-4 border-b flex justify-between items-center">
          <h1 className="text-xl font-bold text-blue-600">UrbanTransit IQ</h1>
          <button className="md:hidden" onClick={() => setMobileOpen(false)}>
            <X size={20} />
          </button>
        </div>
        <nav className="p-4 space-y-1">
          {navItems.map((item) => (
            <Link 
              key={item.name} 
              to={item.path}
              onClick={() => setMobileOpen(false)}
              className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${location.pathname === item.path ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'}`}
            >
              <item.icon size={18} />
              {item.name}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full w-full">
        {/* Top Header */}
        <header className="bg-white border-b p-4 flex items-center justify-between sticky top-0 z-30">
          <div className="flex items-center gap-3">
            <button className="md:hidden text-gray-600" onClick={() => setMobileOpen(true)}>
              <Menu size={24} />
            </button>
            {/* Global Filter Bar Placeholder */}
            <div className="hidden sm:block">
              <span className="text-sm font-medium text-gray-500">Global Filters:</span>
              <select className="ml-2 border rounded-md px-2 py-1 text-sm bg-gray-50">
                <option>All Routes</option>
                <option>R12</option>
              </select>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-700 font-medium hidden sm:inline-block">
              {user.username} <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full ml-1">{user.role}</span>
            </span>
            <button onClick={logout} className="text-red-500 hover:text-red-700 flex items-center gap-1">
              <LogOut size={18} /> <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </header>
        
        {/* Page Content */}
        <div className="flex-1 overflow-auto p-4 md:p-6 w-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
