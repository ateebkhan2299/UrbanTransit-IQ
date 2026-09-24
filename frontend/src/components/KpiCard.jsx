import React from 'react';

const KpiCard = ({ title, value, unit, change, changeType, icon: Icon, color = 'cyan' }) => {
  const colorMap = {
    cyan: 'from-cyan-500/10 to-blue-500/5 text-cyan-400 border-cyan-500/20 icon-bg-cyan-500/20',
    emerald: 'from-emerald-500/10 to-teal-500/5 text-emerald-400 border-emerald-500/20 icon-bg-emerald-500/20',
    amber: 'from-amber-500/10 to-orange-500/5 text-amber-400 border-amber-500/20 icon-bg-amber-500/20',
    rose: 'from-rose-500/10 to-red-500/5 text-rose-400 border-rose-500/20 icon-bg-rose-500/20',
    purple: 'from-purple-500/10 to-indigo-500/5 text-purple-400 border-purple-500/20 icon-bg-purple-500/20',
  };

  const currentStyle = colorMap[color] || colorMap.cyan;

  return (
    <div className={`p-5 glass-card bg-gradient-to-br ${currentStyle} transition-all duration-300 hover:scale-[1.02]`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className="p-2.5 rounded-xl bg-slate-800/80 text-current shadow-inner">
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-3xl font-extrabold text-white tracking-tight">{value}</span>
        {unit && <span className="text-sm font-medium text-slate-400">{unit}</span>}
      </div>

      {change && (
        <div className="mt-2 flex items-center gap-1 text-xs">
          <span className={`font-semibold ${changeType === 'positive' ? 'text-emerald-400' : 'text-rose-400'}`}>
            {change}
          </span>
          <span className="text-slate-500">vs last week</span>
        </div>
      )}
    </div>
  );
};

export default KpiCard;
