import React, { useState } from 'react';
import Header from '../components/Header';
import { simulateWhatIf } from '../api/client';
import { Sliders, Play, ArrowRight, AlertCircle, Info, Activity, Clock, ShieldAlert } from 'lucide-react';

const WhatIf = () => {
  const [selectedRouteId, setSelectedRouteId] = useState('R101');
  const [changeType, setChangeType] = useState('frequency');
  const [changeValue, setChangeValue] = useState(20);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSimulate = (e) => {
    e.preventDefault();
    setLoading(true);
    simulateWhatIf({
      route_id: selectedRouteId,
      change_type: changeType,
      change_value: parseFloat(changeValue),
    })
      .then((res) => setResult(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  return (
    <div>
      <Header
        title="Interactive What-If Scenario Simulator"
        subtitle="Simulate headway frequency, vehicle capacity, and trip scheduling adjustments"
        selectedRouteId={selectedRouteId}
        onSelectRoute={setSelectedRouteId}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Input Parameters Form */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-6">
            <Sliders className="w-5 h-5 text-cyan-400" />
            <h3 className="text-lg font-bold text-white">Simulation Scenario Setup</h3>
          </div>

          <form onSubmit={handleSimulate} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">Target Transit Route</label>
              <input
                type="text"
                value={selectedRouteId}
                onChange={(e) => setSelectedRouteId(e.target.value)}
                placeholder="e.g. R101"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white text-sm focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">Operational Adjustment Type</label>
              <select
                value={changeType}
                onChange={(e) => setChangeType(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-white text-sm focus:outline-none focus:border-cyan-500 font-medium"
              >
                <option value="frequency">Increase Frequency (%)</option>
                <option value="capacity">Vehicle Capacity Scaling (%)</option>
                <option value="add_trip">Add Scheduled Peak Trip</option>
                <option value="remove_trip">Remove Scheduled Off-Peak Trip</option>
              </select>
            </div>

            {changeType === 'frequency' || changeType === 'capacity' ? (
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300 font-semibold">Adjustment Value</span>
                  <span className="text-cyan-400 font-bold">+{changeValue}%</span>
                </div>
                <input
                  type="range"
                  min="-50"
                  max="100"
                  step="5"
                  value={changeValue}
                  onChange={(e) => setChangeValue(e.target.value)}
                  className="w-full accent-cyan-400"
                />
              </div>
            ) : (
              <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/60 text-xs text-slate-300">
                Preset parameters will be applied for trip count modification.
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/25 transition duration-200"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
                  <span>Running Simulation Heuristic...</span>
                </div>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  <span>Execute What-If Simulation</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Results Output Panel */}
        <div className="glass-card p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-emerald-400" />
              <span>Simulation Impact Results</span>
            </h3>

            {result ? (
              <div className="space-y-5">
                {/* Mandatory SRS Estimate Disclaimer */}
                {result.is_estimate && (
                  <div className="p-3 rounded-lg bg-amber-950/40 border border-amber-800/60 text-amber-300 text-xs flex items-start gap-2">
                    <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    <span>
                      <strong>Disclaimer:</strong> The numbers below are simulated estimates generated from operational performance heuristics.
                    </span>
                  </div>
                )}

                {/* Before -> After Metric Comparison Grid */}
                <div className="space-y-4">
                  {/* Occupancy Pct */}
                  <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 flex items-center justify-between">
                    <div>
                      <div className="text-xs text-slate-400 font-semibold">Average Occupancy</div>
                      <div className="text-xs text-slate-500">Route capacity utilization</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-base text-slate-400 line-through">{result.before.occupancy_pct}%</span>
                      <ArrowRight className="w-4 h-4 text-cyan-400" />
                      <span className="text-2xl font-extrabold text-cyan-400">{result.after.occupancy_pct}%</span>
                    </div>
                  </div>

                  {/* Avg Wait Minutes */}
                  <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 flex items-center justify-between">
                    <div>
                      <div className="text-xs text-slate-400 font-semibold">Average Passenger Wait Time</div>
                      <div className="text-xs text-slate-500">Estimated headway wait time</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-base text-slate-400 line-through">{result.before.avg_wait_min}m</span>
                      <ArrowRight className="w-4 h-4 text-emerald-400" />
                      <span className="text-2xl font-extrabold text-emerald-400">{result.after.avg_wait_min}m</span>
                    </div>
                  </div>

                  {/* Overcrowd Risk Pct */}
                  <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 flex items-center justify-between">
                    <div>
                      <div className="text-xs text-slate-400 font-semibold">Overcrowding Risk Level</div>
                      <div className="text-xs text-slate-500">Probability of severe overcrowding</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-base text-slate-400 line-through">{result.before.overcrowd_risk_pct}%</span>
                      <ArrowRight className="w-4 h-4 text-purple-400" />
                      <span className="text-2xl font-extrabold text-purple-400">{result.after.overcrowd_risk_pct}%</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-16 text-slate-500 space-y-2">
                <Sliders className="w-10 h-10 mx-auto text-slate-600 mb-2" />
                <p className="text-sm font-semibold text-slate-400">No active simulation results</p>
                <p className="text-xs text-slate-500">
                  Select a route, adjust scenario parameters, and click "Execute What-If Simulation" to generate before → after operational predictions.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WhatIf;
