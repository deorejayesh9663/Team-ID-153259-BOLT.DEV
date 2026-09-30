import os
import sys
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)

if root_dir not in sys.path:
    sys.path.append(root_dir)

from sim.kasoti_benchmark import KasotiBenchmark

app = FastAPI(title="NETRA Dashboard Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Dashboard connected via WebSocket.")
    
    # Initialize the simulation with VYUHA+AI
    benchmark = KasotiBenchmark(mode="VYUHA+AI", num_robots=20, num_tasks=100, grid_size=30)
    benchmark.setup(seed=104)
    
    try:
        while benchmark.tasks_completed < benchmark.num_tasks and benchmark.ticks < 3000:
            benchmark.step()
            
            # Prepare state payload
            state_payload = {
                "ticks": benchmark.ticks,
                "tasks_completed": benchmark.tasks_completed,
                "num_tasks": benchmark.num_tasks,
                "deadlocks": benchmark.deadlocks,
                "robots": benchmark.robots,
                "tasks_pending": benchmark.tasks_pending,
                "obstacles": list(benchmark.obstacles),
                "dead_zones": benchmark.wifi_dead_zones,
                "blackout": benchmark.blackout,
                "human_actor": benchmark.human_actor,
                "active_planner": benchmark.active_planner,
                "ai_advisor_active": benchmark.ai_advisor_active
            }
            
            await websocket.send_text(json.dumps(state_payload))
            
            # 10 FPS tick rate
            await asyncio.sleep(0.1)
            
        print("Simulation complete. Disconnecting.")
        await websocket.send_text(json.dumps({"status": "COMPLETE"}))
        await websocket.close()
        
    except WebSocketDisconnect:
        print("Dashboard disconnected.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
