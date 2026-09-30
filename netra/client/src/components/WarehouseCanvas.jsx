import React, { useEffect, useRef, useState } from 'react';

export default function WarehouseCanvas({ state, showIntents = true }) {
  const canvasRef = useRef(null);
  const [selectedJunction, setSelectedJunction] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [wasConnected, setWasConnected] = useState(false);

  useEffect(() => {
    const isConnected = !!state;
    if (isConnected && !wasConnected) {
      setIsScanning(true);
      const timer = setTimeout(() => setIsScanning(false), 2000);
      return () => clearTimeout(timer);
    }
    setWasConnected(isConnected);
  }, [state, wasConnected]);
  
  const handleCanvasClick = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    
    // Calculate click position relative to canvas display size
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;
    
    const gridSize = 30;
    const cellSize = canvas.width / gridSize;
    
    const gridX = Math.floor(x / cellSize);
    const gridY = Math.floor(y / cellSize);
    
    if (gridX >= 0 && gridX < gridSize && gridY >= 0 && gridY < gridSize) {
      setSelectedJunction({
        gridX, gridY,
        // Pixel coords for overlay popover
        px: (gridX * cellSize) / scaleX,
        py: (gridY * cellSize) / scaleY,
        cellSize: cellSize / scaleX
      });
    } else {
      setSelectedJunction(null);
    }
  };
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.fillStyle = '#0f172a'; // netra-bg
    ctx.fillRect(0, 0, width, height);
    
    const gridSize = 30; // 30x30 grid from kasoti_benchmark
    const cellSize = width / gridSize;
    
    // Draw Grid (cyberpunk style)
    ctx.strokeStyle = '#1e293b'; // netra-panel
    ctx.lineWidth = 1;
    for (let i = 0; i <= gridSize; i++) {
      ctx.beginPath();
      ctx.moveTo(i * cellSize, 0);
      ctx.lineTo(i * cellSize, height);
      ctx.stroke();
      
      ctx.beginPath();
      ctx.moveTo(0, i * cellSize);
      ctx.lineTo(width, i * cellSize);
      ctx.stroke();
    }
    
    if (!state) return;

    // Draw Dynamic Obstacles (Hazard blocks)
    if (state.obstacles && state.obstacles.length > 0) {
      ctx.fillStyle = 'rgba(239, 68, 68, 0.4)'; // netra-danger transparent
      ctx.strokeStyle = '#ef4444'; // netra-danger
      ctx.lineWidth = 1;
      
      // Draw hazard stripes or just blocks
      state.obstacles.forEach(([x, y]) => {
        ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
        ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
        
        // Hazard cross
        ctx.beginPath();
        ctx.moveTo(x * cellSize, y * cellSize);
        ctx.lineTo((x + 1) * cellSize, (y + 1) * cellSize);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo((x + 1) * cellSize, y * cellSize);
        ctx.lineTo(x * cellSize, (y + 1) * cellSize);
        ctx.stroke();
      });
    }

    // Draw Wi-Fi Dead Zones
    if (state.dead_zones && state.dead_zones.length > 0) {
      ctx.fillStyle = 'rgba(168, 85, 247, 0.2)'; // purple-500 transparent
      ctx.strokeStyle = '#a855f7'; // purple-500
      ctx.lineWidth = 1;
      ctx.setLineDash([5, 5]); // Dashed border for zones
      
      state.dead_zones.forEach(dz => {
        const w = (dz.x_max - dz.x_min + 1) * cellSize;
        const h = (dz.y_max - dz.y_min + 1) * cellSize;
        ctx.fillRect(dz.x_min * cellSize, dz.y_min * cellSize, w, h);
        ctx.strokeRect(dz.x_min * cellSize, dz.y_min * cellSize, w, h);
      });
      ctx.setLineDash([]);
    }

    // Draw Pending Tasks (Amber boxes)
    if (state.tasks_pending) {
      ctx.fillStyle = 'rgba(251, 191, 36, 0.4)'; // netra-warning transparent
      ctx.strokeStyle = '#fbbf24'; // netra-warning
      ctx.lineWidth = 2;
      
      state.tasks_pending.forEach(([x, y]) => {
        // Pixel-art pulse effect for tasks
        const pad = cellSize * 0.2;
        ctx.fillRect(x * cellSize + pad, y * cellSize + pad, cellSize - pad*2, cellSize - pad*2);
        ctx.strokeRect(x * cellSize + pad, y * cellSize + pad, cellSize - pad*2, cellSize - pad*2);
      });
    }

    // Draw Robots (Neon Blue)
    if (state.robots) {
      Object.entries(state.robots).forEach(([, r_data]) => {
        const [x, y] = r_data.pos;
        
        // Robot Body
        ctx.fillStyle = '#38bdf8'; // netra-accent
        ctx.shadowColor = '#38bdf8';
        ctx.shadowBlur = 10;
        
        const pad = cellSize * 0.15;
        ctx.fillRect(x * cellSize + pad, y * cellSize + pad, cellSize - pad*2, cellSize - pad*2);
        
        // Remove shadow for other operations
        ctx.shadowBlur = 0;
        
        // Draw Target Line if moving
        if (r_data.target) {
          const [tx, ty] = r_data.target;
          ctx.strokeStyle = 'rgba(56, 189, 248, 0.3)'; // faded accent
          ctx.lineWidth = 1;
          ctx.setLineDash([5, 5]);
          ctx.beginPath();
          ctx.moveTo(x * cellSize + cellSize/2, y * cellSize + cellSize/2);
          ctx.lineTo(tx * cellSize + cellSize/2, ty * cellSize + cellSize/2);
          ctx.stroke();
          ctx.setLineDash([]);
        }

        // Draw Intent Bubble
        if (showIntents && r_data.intent) {
          ctx.font = '10px "JetBrains Mono", monospace';
          const text = r_data.intent;
          const textWidth = ctx.measureText(text).width;
          
          const bubbleWidth = textWidth + 12;
          const bubbleHeight = 18;
          
          const bx = x * cellSize + cellSize;
          const by = y * cellSize - bubbleHeight/2;
          
          // Bubble Background
          let bubbleColor = 'rgba(30, 41, 59, 0.9)'; // panel bg
          let textColor = '#e5e7eb'; // default white text
          
          if (text === 'Yielding' || text === 'Waiting') {
            bubbleColor = 'rgba(248, 113, 113, 0.2)'; // danger red bg
            textColor = '#f87171';
          } else if (text === 'LiDAR Fallback') {
            bubbleColor = 'rgba(168, 85, 247, 0.2)'; // purple dead zone bg
            textColor = '#a855f7';
          } else if (text === 'SAFE MODE') {
            bubbleColor = 'rgba(239, 68, 68, 0.8)'; // Solid danger red
            textColor = '#ffffff';
          } else if (text === 'CHOKE STORM') {
            bubbleColor = 'rgba(234, 179, 8, 0.9)'; // Solid amber/yellow
            textColor = '#000000';
          } else if (text === 'PACKET LOSS') {
            bubbleColor = 'rgba(217, 119, 6, 0.8)'; // Dark amber
            textColor = '#fef3c7'; // Light amber text
          } else if (text === 'EXPRESS VIP') {
            bubbleColor = 'rgba(168, 85, 247, 0.9)'; // Neon purple
            textColor = '#ffffff';
          } else if (text === 'AI OFFLINE') {
            bubbleColor = 'rgba(220, 38, 38, 0.9)'; // Bright red
            textColor = '#ffffff';
          } else if (text.startsWith('Bid:')) {
            bubbleColor = 'rgba(56, 189, 248, 0.2)'; // accent blue bg
            textColor = '#38bdf8';
          } else if (text === 'Assigned' || text === 'Task Complete') {
            bubbleColor = 'rgba(74, 222, 128, 0.2)'; // success green bg
            textColor = '#4ade80';
          }
          
          ctx.fillStyle = bubbleColor;
          ctx.beginPath();
          ctx.roundRect(bx, by, bubbleWidth, bubbleHeight, 4);
          ctx.fill();
          
          ctx.strokeStyle = textColor;
          ctx.lineWidth = 1;
          ctx.stroke();
          
          // Bubble Text
          ctx.fillStyle = textColor;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(text, bx + bubbleWidth/2, by + bubbleHeight/2);
        }
      });
    }

    // Draw Human Actor
    if (state.human_actor) {
      const [hx, hy] = state.human_actor.pos;
      ctx.fillStyle = '#f472b6'; // pink-400
      ctx.shadowColor = '#f472b6';
      ctx.shadowBlur = 15;
      
      ctx.beginPath();
      ctx.arc(hx * cellSize + cellSize/2, hy * cellSize + cellSize/2, cellSize * 0.4, 0, Math.PI * 2);
      ctx.fill();
      
      ctx.shadowBlur = 0;
      
      // Draw HUMAN label
      if (showIntents) {
        ctx.font = '10px "JetBrains Mono", monospace';
        const text = 'HUMAN';
        const textWidth = ctx.measureText(text).width;
        
        const bubbleWidth = textWidth + 12;
        const bubbleHeight = 18;
        const bx = hx * cellSize + cellSize;
        const by = hy * cellSize - bubbleHeight/2;
        
        ctx.fillStyle = 'rgba(244, 114, 182, 0.2)'; // pink bg
        ctx.beginPath();
        ctx.roundRect(bx, by, bubbleWidth, bubbleHeight, 4);
        ctx.fill();
        
        ctx.strokeStyle = '#f472b6';
        ctx.lineWidth = 1;
        ctx.stroke();
        
        ctx.fillStyle = '#f472b6';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, bx + bubbleWidth/2, by + bubbleHeight/2);
      }
    }

    // Global Blackout Overlay
    if (state.blackout) {
      ctx.fillStyle = 'rgba(153, 27, 27, 0.4)'; // dark red transparent
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      ctx.fillStyle = '#ef4444';
      ctx.font = 'bold 24px monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('CRITICAL SYSTEM FAILURE: BLACKOUT', canvas.width / 2, canvas.height / 2);
    }

  }, [state, showIntents]);

  return (
    <div className="relative glass-panel rounded-xl overflow-hidden p-2">
      <canvas 
        ref={canvasRef}
        onClick={handleCanvasClick}
        width={750} 
        height={750}
        className="block bg-netra-bg rounded-lg cursor-crosshair relative z-0"
        style={{ width: '100%', maxWidth: '750px', aspectRatio: '1/1' }}
      />
      
      {/* Active Planner HUD */}
      {state && state.active_planner && (
        <div className="absolute top-4 left-4 z-20 flex flex-col gap-2 pointer-events-none">
          <div className="bg-gray-900/90 border border-gray-700 rounded p-2 shadow-lg backdrop-blur-sm flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${state.active_planner === 'D* LITE' ? 'bg-netra-accent animate-pulse' : 'bg-amber-500 animate-bounce'}`} />
            <span className="font-mono text-xs font-bold text-gray-300 tracking-wider">
              ROUTING: <span className={state.active_planner === 'D* LITE' ? 'text-netra-accent' : 'text-amber-500'}>{state.active_planner}</span>
            </span>
          </div>
          
          <div className="bg-gray-900/90 border border-gray-700 rounded p-2 shadow-lg backdrop-blur-sm flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${state.ai_advisor_active ? 'bg-green-500 animate-pulse' : 'bg-red-500 animate-ping'}`} />
            <span className="font-mono text-xs font-bold text-gray-300 tracking-wider">
              AI ADVISOR: <span className={state.ai_advisor_active ? 'text-green-500' : 'text-red-500'}>{state.ai_advisor_active ? 'ONLINE' : 'OFFLINE'}</span>
            </span>
          </div>
        </div>
      )}
      
      {/* Radar Sweep Animation (Plays on connection/autonomy toggle) */}
      {isScanning && (
        <div className="absolute inset-2 z-10 pointer-events-none overflow-hidden rounded-lg">
          <div className="absolute top-1/2 left-1/2 w-[200%] h-[200%] -translate-x-1/2 -translate-y-1/2 rounded-full border border-netra-accent/30">
            <div 
              className="w-full h-full animate-radar-sweep"
              style={{
                background: 'conic-gradient(from 0deg at 50% 50%, transparent 0deg, transparent 60deg, rgba(56, 189, 248, 0.1) 80deg, rgba(56, 189, 248, 0.8) 90deg, transparent 90deg)'
              }}
            />
          </div>
          <div className="absolute top-1/2 left-1/2 w-4 h-4 -translate-x-1/2 -translate-y-1/2 rounded-full bg-netra-accent blur-sm" />
        </div>
      )}

      {/* Junction Inspector Overlay */}
      {selectedJunction && (
        <div 
          className="absolute z-10 p-2 bg-gray-900/95 border border-netra-accent/50 rounded shadow-xl pointer-events-none transition-all duration-200"
          style={{ 
            left: `${selectedJunction.px + selectedJunction.cellSize + 10}px`, 
            top: `${selectedJunction.py}px`,
            backdropFilter: 'blur(4px)'
          }}
        >
          <div className="text-[10px] font-mono text-gray-300">
            <div className="text-netra-accent font-bold mb-1 border-b border-gray-700 pb-1">
              JUNCTION [{selectedJunction.gridX}, {selectedJunction.gridY}]
            </div>
            
            {/* Find agents on this junction */}
            {(() => {
              if (!state || !state.robots) return <div className="opacity-50">NO DATA</div>;
              
              const agentsOnJunction = Object.entries(state.robots).filter(
                ([, data]) => data.pos[0] === selectedJunction.gridX && data.pos[1] === selectedJunction.gridY
              );
              
              const agentsTargeting = Object.entries(state.robots).filter(
                ([, data]) => data.target && data.target[0] === selectedJunction.gridX && data.target[1] === selectedJunction.gridY
              );

              return (
                <div className="space-y-1">
                  <div>
                    <span className="text-gray-500">OCCUPANTS: </span>
                    {agentsOnJunction.length > 0 
                      ? agentsOnJunction.map(([id]) => <span key={id} className="text-netra-success">{id} </span>) 
                      : <span className="opacity-50">CLEAR</span>}
                  </div>
                  <div>
                    <span className="text-gray-500">TARGETED BY: </span>
                    {agentsTargeting.length > 0 
                      ? agentsTargeting.map(([id]) => <span key={id} className="text-netra-warning">{id} </span>) 
                      : <span className="opacity-50">NONE</span>}
                  </div>
                </div>
              );
            })()}
          </div>
        </div>
      )}
      
      {/* Decorative corners */}
      <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-netra-accent rounded-tl-xl pointer-events-none" />
      <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-netra-accent rounded-tr-xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-netra-accent rounded-bl-xl pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-netra-accent rounded-br-xl pointer-events-none" />
    </div>
  );
}
