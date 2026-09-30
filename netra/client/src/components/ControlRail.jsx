import React from 'react';
import { Pause, AlertOctagon, Gamepad2, Box, WifiOff, Lock } from 'lucide-react';

export default function ControlRail() {
  const buttons = [
    { label: 'PAUSE', icon: <Pause className="w-4 h-4" /> },
    { label: 'E-STOP', icon: <AlertOctagon className="w-4 h-4" /> },
    { label: 'TELEOP', icon: <Gamepad2 className="w-4 h-4" /> },
    { label: 'DROP OBSTACLE', icon: <Box className="w-4 h-4" /> },
    { label: 'KILL WIFI', icon: <WifiOff className="w-4 h-4" /> }
  ];

  return (
    <div className="flex gap-4 mb-4 w-full max-w-[750px] items-center justify-between bg-netra-panel/50 p-2 rounded-lg border border-gray-700/50 backdrop-blur-sm relative">
      
      {/* Read-Only Badge */}
      <div className="absolute -top-3 left-4 bg-gray-900 border border-gray-700 text-gray-500 px-2 py-0.5 text-[9px] font-mono tracking-widest flex items-center gap-1 rounded shadow-md z-10">
        <Lock className="w-3 h-3 text-netra-danger" />
        <span className="text-netra-danger font-bold">OVERRIDE DISABLED</span> (TELEMETRY TAP ONLY)
      </div>

      {buttons.map((btn) => (
        <button
          key={btn.label}
          disabled
          className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded border border-gray-800 text-gray-600 bg-gray-900/50 cursor-not-allowed font-mono text-[10px] tracking-widest`}
          onClick={() => console.log(`[CONTROL] Triggered ${btn.label}`)}
        >
          {btn.icon}
          {btn.label}
        </button>
      ))}
    </div>
  );
}
