import React from 'react';

export default function RouteMap() {
  return (
    <div className="h-full flex flex-col space-y-4 w-full">
      <h1 className="text-2xl font-bold text-gray-800 shrink-0">Route Map</h1>
      
      {/* Map Container */}
      <div className="flex-1 bg-gray-200 rounded-lg shadow-inner flex items-center justify-center min-h-[400px]">
        <p className="text-gray-500 text-center px-4">
          Map rendering requires React-Leaflet integration.<br/>
          (Responsive map container ready. Install map tiles here.)
        </p>
      </div>
    </div>
  );
}
