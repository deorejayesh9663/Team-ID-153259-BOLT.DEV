import time

class BaselineRobot:
    def __init__(self, robot_id, x, y, path):
        self.robot_id = robot_id
        self.x = x
        self.y = y
        self.path = path
        
    def tick(self, peers):
        if not self.path:
            return
            
        next_x, next_y = self.path[0]
        
        # Baseline stop-and-wait collision check
        for p in peers:
            if p.robot_id != self.robot_id and p.x == next_x and p.y == next_y:
                print(f"[{self.robot_id}] Blocked by {p.robot_id} at ({next_x}, {next_y}). Stopping and waiting...")
                return # Stop and wait indefinitely (NO PIBT)
                
        # Move
        self.x = next_x
        self.y = next_y
        self.path.pop(0)
        print(f"[{self.robot_id}] Moved to ({self.x}, {self.y})")

if __name__ == "__main__":
    print("Testing Baseline Stop-and-Wait (Strawman)...")
    
    # Same topology that Vyuha solved in T-P3-03
    # R1 at (0,0) wants to go to (1,0)
    # R2 at (1,0) wants to go to (0,0)
    r1 = BaselineRobot("AMR_1", 0, 0, [(1, 0), (2, 0)])
    r2 = BaselineRobot("AMR_2", 1, 0, [(0, 0), (0, 1)])
    
    robots = [r1, r2]
    
    for tick_num in range(5):
        print(f"--- TICK {tick_num} ---")
        for r in robots:
            r.tick(robots)
            
        # Check if they are permanently stuck
        # If no robot moves for 2 consecutive ticks, it's gridlocked.
    
    assert r1.path and r2.path, "Both robots should be stuck with unfinished paths."
    print("\nSUCCESS (Validation): Complete gridlock! Baseline stop-and-wait fails in narrow aisles without PIBT.")
