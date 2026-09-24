import React, { useState } from 'react';
import { Search, Filter, Calendar } from 'lucide-react';

const SearchFilterBar = ({ onFilterChange }) => {
  const [filters, setFilters] = useState({
    dateRange: '',
    route: '',
    stop: '',
    vehicle: '',
    direction: '',
    peakToggle: 'all', // 'all', 'peak', 'offpeak'
    delaySeverity: 'all', // 'all', 'ontime', 'minor', 'moderate', 'major', 'severe'
    occupancyLevel: 'all', // 'all', 'low', 'medium', 'high', 'overcrowded'
  });

  const handleChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    if (onFilterChange) onFilterChange(newFilters);
  };

  return (
    <div className="glass-card p-4 mb-6">
      <div className="flex flex-wrap items-center gap-4">
        {/* Date Range */}
        <div className="flex-1 min-w-[150px]">
          <label className="block text-xs text-slate-400 mb-1">Date Range</label>
          <div className="relative">
            <Calendar className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
            <input 
              type="date"
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
              value={filters.dateRange}
              onChange={(e) => handleChange('dateRange', e.target.value)}
            />
          </div>
        </div>

        {/* Route Select */}
        <div className="flex-1 min-w-[150px]">
          <label className="block text-xs text-slate-400 mb-1">Route</label>
          <select 
            className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
            value={filters.route}
            onChange={(e) => handleChange('route', e.target.value)}
          >
            <option value="">All Routes</option>
            <option value="R001">Route 1 (Downtown)</option>
            <option value="R002">Route 2 (Uptown)</option>
          </select>
        </div>

        {/* Stop Select */}
        <div className="flex-1 min-w-[150px]">
          <label className="block text-xs text-slate-400 mb-1">Stop</label>
          <input 
            type="text"
            placeholder="Search stop..."
            className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
            value={filters.stop}
            onChange={(e) => handleChange('stop', e.target.value)}
          />
        </div>

        {/* Peak / Off-Peak */}
        <div className="flex-1 min-w-[150px]">
          <label className="block text-xs text-slate-400 mb-1">Time Period</label>
          <select 
            className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
            value={filters.peakToggle}
            onChange={(e) => handleChange('peakToggle', e.target.value)}
          >
            <option value="all">All Day</option>
            <option value="peak">Peak Hours</option>
            <option value="offpeak">Off-Peak</option>
          </select>
        </div>
        
        {/* Additional dropdowns for delay and occupancy that dashboards can use */}
        <div className="flex-1 min-w-[150px]">
          <label className="block text-xs text-slate-400 mb-1">Delay Severity</label>
          <select 
            className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
            value={filters.delaySeverity}
            onChange={(e) => handleChange('delaySeverity', e.target.value)}
          >
            <option value="all">All</option>
            <option value="ontime">On Time</option>
            <option value="minor">Minor (&lt;5 min)</option>
            <option value="major">Major (&gt;15 min)</option>
          </select>
        </div>

      </div>
    </div>
  );
};

export default SearchFilterBar;
