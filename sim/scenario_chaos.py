import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from vyuha.samvaad.deadlock import WaitForGraph

class ChaosRobot:
    def __init__(self, robot_id, x, y, path):
        self.robot_id = robot_id
        self.x = x
        self.y = y
        self.path = path
        self.history = [(x, y)]
        self.waiting_on = None
        # Priority: lower number is higher priority. (e.g. AMR_1 = 1)
        self.priority = int(robot_id.split('_')[1])
        
    def tick(self, peers):
        if not self.path:
            return
            
        next_x, next_y = self.path[0]
        
        # Check if next cell is occupied by a peer
        blocked_by = None
        for p in peers:
            if p.robot_id != self.robot_id and p.x == next_x and p.y == next_y:
                blocked_by = p.robot_id
                break
                
        if blocked_by:
            self.waiting_on = blocked_by
            print(f"[{self.robot_id}] Blocked by {blocked_by} at ({next_x}, {next_y})")
        else:
            self.waiting_on = None
            self.x, self.y = self.path.pop(0)
            self.history.append((self.x, self.y))
            print(f"[{self.robot_id}] Moved to ({self.x}, {self.y})")

    def reverse(self):
        # Reverse 1 cell based on history
        if len(self.history) > 1:
            self.history.pop() # remove current
            prev_x, prev_y = self.history[-1]
            print(f"[{self.robot_id}] REVERSING to ({prev_x}, {prev_y}) and yielding!")
            # Insert current back into path so we visit it again after yielding
            self.path.insert(0, (self.x, self.y))
            self.x, self.y = prev_x, prev_y
            self.waiting_on = None

if __name__ == "__main__":
    print("Testing Reverse-and-Yield Recovery...")
    
    # Force deadlock:
    # R1 at (0,0) wants to go to (1,0)
    # R2 at (1,0) wants to go to (0,0)
    r1 = ChaosRobot("AMR_1", 0, 0, [(1, 0), (2, 0)])
    r2 = ChaosRobot("AMR_2", 1, 0, [(0, 0), (0, 1)])
    
    # Give R2 a fake history so it can reverse to a siding at (1,1)
    r2.history = [(1, 1), (1, 0)]
    
    robots = [r1, r2]
    
    for tick in range(10):
        print(f"--- TICK {tick} ---")
        # Tick all robots
        for r in robots:
            r.tick(robots)
            
        # Deadlock Detection
        wfg = WaitForGraph()
        for r in robots:
            if r.waiting_on:
                wfg.add_intent(r.robot_id, r.waiting_on)
                
        sccs = wfg.find_sccs()
        deadlocks = [s for s in sccs if len(s) > 1]
        
        if deadlocks:
            print(f"Deadlock detected: {deadlocks[0]}")
            # Resolve: lower priority (higher ID number) reverses
            involved_robots = [r for r in robots if r.robot_id in deadlocks[0]]
            involved_robots.sort(key=lambda r: r.priority, reverse=True)
            victim = involved_robots[0]
            victim.reverse()
            
        if all(not r.path for r in robots):
            print("SUCCESS: Both robots completed their paths without permanent deadlock.")
            sys.exit(0)
            
    print("FAILED: Deadlock was not resolved within 10 ticks.")
    sys.exit(1)
