import React from 'react';
import { Activity, Server, Target, AlertTriangle } from 'lucide-react';

export default function StatusRail({ state, connectionStatus }) {
  
  const getStatusColor = () => {
    switch(connectionStatus) {
      case 'Connected': return 'text-netra-success';
      case 'Disconnected': return 'text-gray-500';
      case 'Error': return 'text-netra-danger';
      case 'Complete': return 'text-netra-accent';
      default: return 'text-gray-500';
    }
  };

  return (
    <div className="w-64 glass-panel h-full flex flex-col p-4 border-r border-y-0 border-l-0 border-gray-700/50">
      
      {/* Brand Header */}
      <div className="flex items-center gap-2 mb-8 mt-2">
        <div className="w-8 h-8 rounded-full bg-netra-accent/20 flex items-center justify-center border border-netra-accent/50">
          <Activity className="w-4 h-4 text-netra-accent animate-pulse" />
        </div>
        <h1 className="text-xl font-bold tracking-widest bg-clip-text text-transparent bg-gradient-to-r from-gray-100 to-gray-500">
          NETRA
        </h1>
      </div>

      {/* Connection Status */}
      <div className="mb-8">
        <h2 className="text-xs uppercase tracking-wider text-gray-500 mb-3">Gateway</h2>
        <div className="flex items-center gap-3">
          <Server className={`w-5 h-5 ${getStatusColor()}`} />
          <span className={`font-semibold ${getStatusColor()}`}>
            {connectionStatus}
          </span>
        </div>
      </div>

      {/* Telemetry Metrics */}
      <div className="flex-1">
        <h2 className="text-xs uppercase tracking-wider text-gray-500 mb-4">Telemetry</h2>
        
        <div className="space-y-6">
          
          {/* Ticks */}
          <div>
            <div className="flex items-center justify-between text-sm text-gray-400 mb-1">
              <span>Simulation Ticks</span>
              <span className="font-mono text-netra-accent">
                {state ? state.ticks : '0'} / 3000
              </span>
            </div>
            <div className="h-1.5 w-full bg-gray-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-netra-accent transition-all duration-300"
                style={{ width: `${state ? Math.min((state.ticks / 3000) * 100, 100) : 0}%` }}
              />
            </div>
          </div>

          {/* Tasks */}
          <div>
            <div className="flex items-center justify-between text-sm text-gray-400 mb-1">
              <span className="flex items-center gap-1.5"><Target className="w-4 h-4" /> Tasks</span>
              <span className="font-mono text-netra-success">
                {state ? state.tasks_completed : '0'} / {state ? state.num_tasks : '100'}
              </span>
            </div>
            <div className="h-1.5 w-full bg-gray-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-netra-success transition-all duration-300"
                style={{ width: `${state ? (state.tasks_completed / state.num_tasks) * 100 : 0}%` }}
              />
            </div>
          </div>

          {/* PIBT Yields */}
          <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700/50">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-netra-warning" />
                PIBT Yields
              </span>
              <span className="font-mono text-lg text-netra-warning font-bold">
                {state ? state.deadlocks : '0'}
              </span>
            </div>
          </div>

        </div>
      </div>

      {/* Footer info */}
      <div className="mt-auto pt-4 border-t border-gray-700/50 text-xs text-gray-600 font-mono">
        VYUHA+AI EDGE ADVISORY
      </div>
    </div>
  );
}
