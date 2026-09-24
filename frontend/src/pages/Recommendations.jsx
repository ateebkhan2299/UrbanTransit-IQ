import React from 'react';

export default function Recommendations() {
  const recs = [
    {
      "recommendation_id": "REC-0001",
      "action": "Increase Route R12 frequency between 08:00 and 09:00",
      "priority": "Critical",
      "route_id": "R12",
      "reason": {
          "average_occupancy_pct": 94,
          "critical_occupancy_events": 18
      }
    }
  ];

  return (
    <div className="space-y-6 w-full max-w-full">
      <h1 className="text-2xl font-bold text-gray-800">Recommendations & What-If Simulator</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Feed - takes full width on mobile, 2 cols on lg */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold text-gray-700">Actionable Insights</h2>
          {recs.map(rec => (
            <div key={rec.recommendation_id} className="bg-white border rounded-lg p-4 shadow-sm">
              <div className="flex flex-col sm:flex-row justify-between sm:items-start gap-2 mb-2">
                <h3 className="font-medium text-gray-900">{rec.action}</h3>
                <span className="bg-red-100 text-red-700 px-2 py-1 rounded text-xs font-semibold self-start sm:self-auto">
                  {rec.priority}
                </span>
              </div>
              <p className="text-sm text-gray-500 mb-2">Route: {rec.route_id}</p>
              <div className="bg-gray-50 p-3 rounded text-sm text-gray-700 border">
                <strong>Evidence:</strong> Avg Occupancy {rec.reason.average_occupancy_pct}%, Events: {rec.reason.critical_occupancy_events}
              </div>
            </div>
          ))}
        </div>

        {/* What-If Form */}
        <div className="bg-white border rounded-lg p-4 shadow-sm self-start">
          <h2 className="text-lg font-semibold text-gray-700 mb-4">What-If Simulator</h2>
          <form className="space-y-4">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Route ID</label>
              <input className="w-full border rounded p-2" defaultValue="R12" />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">New Frequency (trips/day)</label>
              <input type="number" className="w-full border rounded p-2" defaultValue={30} />
            </div>
            <button className="w-full bg-blue-600 text-white rounded p-2 hover:bg-blue-700 transition">
              Simulate Impact
            </button>
          </form>
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
            <strong>*ESTIMATED* Impact:</strong> Wait time reduces to 20m.
            <br/><span className="text-xs">Disclaimer: These are simulated projections.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
