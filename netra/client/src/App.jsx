import { useState, useEffect } from 'react';
import StatusRail from './components/StatusRail';
import WarehouseCanvas from './components/WarehouseCanvas';
import FleetStrip from './components/FleetStrip';
import RobotDrawer from './components/RobotDrawer';
import ControlRail from './components/ControlRail';

function App() {
  const [gameState, setGameState] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/telemetry');

    ws.onopen = () => {
      setConnectionStatus('Connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.status === "COMPLETE") {
          setConnectionStatus('Complete');
        } else {
          setGameState(data);
        }
      } catch (err) {
        console.error("Failed to parse websocket message", err);
      }
    };

    ws.onclose = () => {
      setConnectionStatus('Disconnected');
    };

    ws.onerror = (err) => {
      console.error("WebSocket error", err);
      setConnectionStatus('Error');
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-netra-bg text-gray-200">
      {/* Left Sidebar - Status Rail */}
      <StatusRail state={gameState} connectionStatus={connectionStatus} />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col items-center justify-center relative p-8 pb-10">
        
        {/* Top Control Rail */}
        <ControlRail />

        {/* Viewport canvas */}
        <WarehouseCanvas state={gameState} />
        
        <h1 className="text-4xl font-bold tracking-widest text-netra-accent/10 absolute top-8 right-8 pointer-events-none">
          NETRA VYUHA+AI
        </h1>
      </main>

      {/* Right Sidebar - Robot Drawer */}
      <RobotDrawer state={gameState} />

      {/* Bottom Ticker */}
      <FleetStrip state={gameState} />
    </div>
  );
}

export default App;
