import React, { useState, useEffect } from 'react';
import { Terminal, Cpu, Network, ListTree, Bot } from 'lucide-react';

export default function RobotDrawer({ state }) {
  const [activeTab, setActiveTab] = useState('TRACES');
  const [selectedRobot] = useState('AMR_0');
  const [traces, setTraces] = useState([]);

  // We can just grab the first robot if selected isn't there, or keep it fixed
  const robotData = state && state.robots ? state.robots[selectedRobot] : null;

  // Clear traces when selected robot changes
  useEffect(() => {
    setTraces([]);
  }, [selectedRobot]);

  // Accumulate traces
  useEffect(() => {
    if (robotData && robotData.intent && robotData.intent !== "Waiting") {
      setTraces(prev => {
        const newTrace = `[T=${state.ticks}] ${robotData.intent}`;
        if (prev.length > 0 && prev[0] === newTrace) return prev;
        return [newTrace, ...prev].slice(0, 50); // Keep last 50 traces, newest first
      });
    }
  }, [state?.ticks, robotData]);

  const tabs = [
    { id: 'TERMINAL', icon: <Terminal className="w-4 h-4" /> },
    { id: 'BUILD', icon: <Cpu className="w-4 h-4" /> },
    { id: 'MESH', icon: <Network className="w-4 h-4" /> },
    { id: 'TRACES', icon: <ListTree className="w-4 h-4" /> },
  ];

  return (
    <div className="w-80 glass-panel h-full flex flex-col p-4 border-l border-y-0 border-r-0 border-gray-700/50">
      
      {/* Drawer Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2 text-gray-300">
          <Bot className="w-5 h-5 text-netra-accent" />
          <h2 className="font-bold tracking-wider">INSPECTOR</h2>
        </div>
        
        {/* Robot Selector (Mocked as a simple display for now) */}
        <div className="px-2 py-1 rounded bg-gray-800 border border-gray-700 text-xs text-netra-accent font-mono">
          {selectedRobot}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-4 p-1 bg-gray-800/50 rounded-lg">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 flex flex-col items-center justify-center py-2 rounded-md transition-colors ${
              activeTab === tab.id 
                ? 'bg-gray-700 text-white shadow-sm' 
                : 'text-gray-500 hover:text-gray-300 hover:bg-gray-700/50'
            }`}
          >
            {tab.icon}
            <span className="text-[10px] mt-1 font-semibold">{tab.id}</span>
          </button>
        ))}
      </div>

      {/* Tab Content Area */}
      <div className="flex-1 bg-gray-900/50 border border-gray-700/50 rounded-lg p-3 font-mono text-xs overflow-y-auto">
        
        {activeTab === 'TERMINAL' && (
          <div className="text-gray-400 space-y-2">
            <p className="text-netra-success">&gt;{selectedRobot} online.</p>
            {robotData ? (
              <>
                <p>&gt;Pos: [{robotData.pos[0]}, {robotData.pos[1]}]</p>
                <p>&gt;Target: {robotData.target ? `[${robotData.target[0]}, ${robotData.target[1]}]` : 'IDLE'}</p>
                <p>&gt;Intent: {robotData.intent || 'NOMINAL'}</p>
                <p>&gt;Priority: {robotData.priority}</p>
              </>
            ) : (
              <p className="animate-pulse">Waiting for telemetry...</p>
            )}
          </div>
        )}

        {activeTab === 'BUILD' && (
          <div className="text-gray-400 space-y-4">
            <div>
              <span className="text-netra-accent">Model:</span> CONGESTION_GRU_v2
              <div className="h-1 w-full bg-gray-800 mt-1 rounded"><div className="h-full bg-netra-accent w-3/4 rounded"></div></div>
            </div>
            <div>
              <span className="text-netra-warning">Weights:</span> PRIORITY_TREE_INT8
              <div className="h-1 w-full bg-gray-800 mt-1 rounded"><div className="h-full bg-netra-warning w-full rounded"></div></div>
            </div>
          </div>
        )}

        {activeTab === 'MESH' && (
          <div className="text-gray-400 flex flex-col items-center justify-center h-full opacity-50">
            <Network className="w-8 h-8 mb-2" />
            <p>PIBT Dependency Graph</p>
            <p>(Select multiple agents)</p>
          </div>
        )}

        {activeTab === 'TRACES' && (
          <div className="text-gray-400">
            <p className="text-netra-success mb-4 sticky top-0 bg-gray-900 pb-2 border-b border-gray-700/50">
              Decision Log [TRACES]
            </p>
            <div className="space-y-1">
              {traces.length > 0 ? traces.map((trace, idx) => (
                <p key={idx} className={
                  trace.includes("Yielding") ? "text-netra-danger" : 
                  trace.includes("Bid:") ? "text-netra-accent" : 
                  trace.includes("Assigned") || trace.includes("Complete") ? "text-netra-success" : 
                  "text-gray-400 opacity-70"
                }>
                  {trace}
                </p>
              )) : (
                <p className="opacity-50 animate-pulse">Awaiting telemetry...</p>
              )}
            </div>
          </div>
        )}

      </div>
      
    </div>
  );
}
