import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from warehouse import WarehouseMap
from planner import AStarPlanner
from physics import check_footprint_collision
from vyuha.samvaad.arbiter import SpaceTimeTable, Arbiter

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

class CooperativeRobot:
    def __init__(self, robot_id, x, y):
        self.robot_id = robot_id
        self.x = x
        self.y = y
        self.time_path = {} # maps t -> (x, y)
        self.size = (0.9, 0.4) # Slightly smaller than 1.0 to avoid false positive touching on adj cells

    def plan_and_reserve(self, goal, start_time, planner, arbiter):
        path_2d = planner.plan((self.x, self.y), goal)
        if not path_2d:
            return False
            
        current_t = start_time
        self.time_path[current_t] = path_2d[0]
        arbiter.table.reserve(self.robot_id, path_2d[0][0], path_2d[0][1], current_t)
        
        for i in range(1, len(path_2d)):
            prev_x, prev_y = path_2d[i-1]
            next_x, next_y = path_2d[i]
            
            requested_t = current_t + 1
            actual_t = arbiter.request_reservation(self.robot_id, next_x, next_y, requested_time=requested_t)
            
            # fill waiting time
            for wait_t in range(requested_t, actual_t):
                arbiter.table.reserve(self.robot_id, prev_x, prev_y, wait_t)
                self.time_path[wait_t] = (prev_x, prev_y)
                
            self.time_path[actual_t] = (next_x, next_y)
            current_t = actual_t
            
        return True

    def get_pose_at(self, t):
        if t in self.time_path:
            return (self.time_path[t][0], self.time_path[t][1], 0)
        
        max_t = max(self.time_path.keys()) if self.time_path else 0
        if t > max_t and self.time_path:
            return (self.time_path[max_t][0], self.time_path[max_t][1], 0)
            
        return (self.x, self.y, 0)

if __name__ == "__main__":
    print("Running 3-AMR Scenario...")
    map_path = os.path.join(current_dir, "maps", "small_3amr.json")
    warehouse = WarehouseMap(map_path)
    planner = AStarPlanner(warehouse)
    
    table = SpaceTimeTable()
    arbiter = Arbiter(table)
    
    # AMR_1: Vertical from top to bottom. (7,0) -> (7,14). Reaches (7,4) at t=4.
    r1 = CooperativeRobot("AMR_1", 7, 0)
    # AMR_2: Horizontal from left to right. Start at (3,4) so it reaches (7,4) at t=4.
    r2 = CooperativeRobot("AMR_2", 3, 4)
    # AMR_3: Horizontal from right to left. (19,10) -> (0,10). Reaches (7,10) at t=12.
    # AMR_1 reaches (7,10) at t=10. No conflict.
    # Let's adjust AMR_3 to start at (17,10) so it travels 10 cells to (7,10), arriving at t=10.
    r3 = CooperativeRobot("AMR_3", 17, 10)
    
    print("Assigning intersecting paths...")
    r1.plan_and_reserve((7, 14), 0, planner, arbiter)
    r2.plan_and_reserve((19, 4), 0, planner, arbiter)
    r3.plan_and_reserve((0, 10), 0, planner, arbiter)
    
    max_time = max(
        max(r1.time_path.keys()) if r1.time_path else 0,
        max(r2.time_path.keys()) if r2.time_path else 0,
        max(r3.time_path.keys()) if r3.time_path else 0
    )
    
    collisions = 0
    for t in range(max_time + 1):
        p1 = r1.get_pose_at(t)
        p2 = r2.get_pose_at(t)
        p3 = r3.get_pose_at(t)
        
        if check_footprint_collision(p1, r1.size, p2, r2.size):
            print(f"Collision between AMR_1 and AMR_2 at t={t}")
            collisions += 1
        if check_footprint_collision(p1, r1.size, p3, r3.size):
            print(f"Collision between AMR_1 and AMR_3 at t={t}")
            collisions += 1
        if check_footprint_collision(p2, r2.size, p3, r3.size):
            print(f"Collision between AMR_2 and AMR_3 at t={t}")
            collisions += 1
            
    print(f"Total footprint collisions: {collisions}")
    if collisions == 0:
        print("SUCCESS: 3 robots planned intersecting paths, Arbiter resolved conflicts, 0 footprint collisions.")
    else:
        print("FAILED: Collisions detected.")
        sys.exit(1)
