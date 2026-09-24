import React from 'react';
import LiveSyncIndicator from './LiveSyncIndicator';
import NotificationBell from './NotificationBell';
import GlobalRouteSelector from './GlobalRouteSelector';

const Header = ({ title, subtitle, selectedRouteId, onSelectRoute }) => {
  return (
    <header className="flex flex-col md:flex-row md:items-center justify-between pb-6 mb-6 border-b border-slate-800 gap-4">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">{title}</h2>
        {subtitle && <p className="text-sm text-slate-400 mt-1">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4 flex-wrap">
        <GlobalRouteSelector
          selectedRouteId={selectedRouteId}
          onSelectRoute={onSelectRoute}
        />
        <LiveSyncIndicator />
        <NotificationBell />
      </div>
    </header>
  );
};

export default Header;
