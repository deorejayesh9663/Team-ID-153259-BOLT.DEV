import React, { useMemo } from 'react';
import { Radio } from 'lucide-react';

export default function FleetStrip({ state }) {
  // Extract interesting events to show on the ticker
  const events = useMemo(() => {
    if (!state || !state.robots) return ["WAITING FOR TELEMETRY..."];
    
    const activeEvents = [];
    Object.entries(state.robots).forEach(([r_id, data]) => {
      if (data.intent && data.intent !== "Waiting" && data.intent !== "Task Complete") {
        activeEvents.push(`${r_id} > ${data.intent.toUpperCase()}`);
      }
    });

    if (activeEvents.length === 0) {
      activeEvents.push("SYSTEM NOMINAL - ALL AGENTS OPTIMAL");
    }

    return activeEvents;
  }, [state]);

  return (
    <div className="absolute bottom-0 left-64 right-0 h-10 glass-panel border-t border-gray-700/50 flex items-center overflow-hidden z-10 text-xs font-mono">
      
      {/* Fixed label on the left */}
      <div className="flex items-center gap-2 bg-netra-panel h-full px-4 border-r border-gray-700/50 text-netra-accent z-20 shadow-[10px_0_20px_-10px_rgba(0,0,0,0.5)] whitespace-nowrap">
        <Radio className="w-4 h-4 animate-pulse" />
        <span className="font-bold tracking-widest">FLEET COMMS</span>
      </div>

      {/* Marquee Ticker */}
      <div className="flex-1 overflow-hidden relative h-full flex items-center">
        <div className="absolute whitespace-nowrap animate-[ticker_30s_linear_infinite] hover:[animation-play-state:paused] flex gap-8 px-4">
          
          {/* Duplicate the events list to create a seamless loop effect */}
          {[...events, ...events, ...events].map((evt, idx) => {
            let colorClass = "text-gray-400";
            if (evt.includes("YIELDING")) colorClass = "text-netra-danger font-bold";
            if (evt.includes("ASSIGNED")) colorClass = "text-netra-success";
            if (evt.includes("BID")) colorClass = "text-netra-accent";
            if (evt.includes("NOMINAL")) colorClass = "text-netra-success tracking-widest";

            return (
              <span key={idx} className={`flex items-center gap-3 ${colorClass}`}>
                <span className="w-1.5 h-1.5 rounded-full bg-current opacity-50" />
                {evt}
              </span>
            );
          })}
        </div>
      </div>
      
    </div>
  );
}
