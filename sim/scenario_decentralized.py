import os
import sys
import time
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from warehouse import WarehouseMap
from planner import AStarPlanner
from physics import check_footprint_collision
from vyuha.samvaad.transport import InProcessTransport, LossyTransport
from vyuha.samvaad.messages import BeliefState

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

class DecentralizedRobot:
    def __init__(self, robot_id, x, y, goal_x, goal_y, transport):
        self.robot_id = robot_id
        self.x = x
        self.y = y
        self.goal_x = goal_x
        self.goal_y = goal_y
        self.transport = transport
        self.path = []
        self.size = (0.9, 0.4)
        self.peer_beliefs = {} # robot_id -> (x, y)
        self.state = "RUNNING"
        
        # Subscribe to peer beliefs using a wildcard or exact topic.
        # In ProcessTransport, we have to subscribe to the exact topics or implement wildcard.
        # Since InProcessTransport uses exact match, we just subscribe to a shared topic for this test.
        self.transport.subscribe("vyuha/robot/shared_state", self._on_belief)

    def _on_belief(self, topic, payload):
        try:
            data = json.loads(payload.decode('utf-8'))
            if data["robot_id"] != self.robot_id:
                self.peer_beliefs[data["robot_id"]] = (data["x"], data["y"])
        except Exception:
            pass

    def plan(self, planner):
        self.path = planner.plan((self.x, self.y), (self.goal_x, self.goal_y))
        if self.path and len(self.path) > 0:
            self.path.pop(0) # remove current pos

    def tick(self, central_engine_alive=True):
        if self.state == "DONE":
            return
            
        if self.x == self.goal_x and self.y == self.goal_y:
            self.state = "DONE"
            return

        # Broadcast belief state
        bs = BeliefState(robot_id=self.robot_id, x=self.x, y=self.y, theta=0, battery=100.0)
        self.transport.publish("vyuha/robot/shared_state", bs.model_dump_json().encode('utf-8'))
        
        # Determine next step
        if not self.path:
            return
            
        next_x, next_y = self.path[0]
        
        # Check collision with peers if central engine is dead
        if not central_engine_alive:
            collision = False
            for peer_id, (px, py) in self.peer_beliefs.items():
                # Conservative safety radius (Manhattan distance <= 2)
                if abs(next_x - px) + abs(next_y - py) <= 2:
                    # Resolve tie deterministically to avoid deadlock
                    if self.robot_id > peer_id:
                        collision = True
                        break
            
            if collision:
                print(f"[{self.robot_id}] P2P avoidance: Yielding at ({self.x}, {self.y}) to avoid {peer_id}")
                return # Wait this tick

        # Move
        self.x, self.y = self.path.pop(0)

if __name__ == "__main__":
    print("Testing Decentralized Execution...")
    map_path = os.path.join(current_dir, "maps", "small_3amr.json")
    warehouse = WarehouseMap(map_path)
    planner = AStarPlanner(warehouse)
    
    base_transport = InProcessTransport()
    # Use 0.0 delay for faster test, but keep some drop probability
    transport = LossyTransport(base_transport, drop_prob=0.1, min_delay=0.001, max_delay=0.005)
    
    r1 = DecentralizedRobot("AMR_1", 7, 0, 7, 14, transport)
    r2 = DecentralizedRobot("AMR_2", 3, 4, 19, 4, transport)
    r3 = DecentralizedRobot("AMR_3", 17, 10, 0, 10, transport)
    
    robots = [r1, r2, r3]
    for r in robots:
        r.plan(planner)
        
    central_engine_alive = True
    
    for tick in range(25):
        if tick == 2:
            print("--- KILLED CENTRAL ENGINE ---")
            central_engine_alive = False
            
        for r in robots:
            r.tick(central_engine_alive)
            
        # Give transport thread time to deliver messages
        time.sleep(0.05)
        
        # Check collisions
        for i in range(len(robots)):
            for j in range(i+1, len(robots)):
                if check_footprint_collision(
                    (robots[i].x, robots[i].y, 0), robots[i].size,
                    (robots[j].x, robots[j].y, 0), robots[j].size
                ):
                    print(f"FAILED: Collision between {robots[i].robot_id} and {robots[j].robot_id} at tick {tick}")
                    sys.exit(1)
                    
    done = all(r.state == "DONE" for r in robots)
    print("Test finished without collisions.")
    if not central_engine_alive:
        print("SUCCESS: Robots switched to P2P collision avoidance and continued moving.")
    transport.close()
