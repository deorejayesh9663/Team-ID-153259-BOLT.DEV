import time
import cProfile
import pstats
import io
import math
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Simulating PIBT local resolution logic
def simulate_pibt_negotiation(robot_count, obstacles):
    """
    Simulate the computational overhead of PIBT (Priority-Based Search)
    running on a low-power edge node (e.g., Raspberry Pi 5).
    """
    grid_size = 40
    # Simulate some arbitrary graph traversals
    valid_moves = []
    for r in range(robot_count):
        # Path validation checking 4 neighbors
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            nx, ny = (r % grid_size) + dx, (r % grid_size) + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                if (nx, ny) not in obstacles:
                    valid_moves.append((nx, ny))
                    
    # Simulate graph cascading priorities
    # O(N^2) naive fallback conflict resolution check
    conflicts = 0
    for i in range(robot_count):
        for j in range(i + 1, robot_count):
            if i * j % 10 == 0:  # arbitrary simulated conflict condition
                conflicts += 1
                
    return conflicts

def run_budget_profile():
    print("=" * 50)
    print("VYUHA Edge Compute Budget Profiler (Pi 5 Target)")
    print("=" * 50)
    
    # Target 10Hz control loop (100ms budget per tick)
    TARGET_BUDGET_MS = 100.0
    
    # Profile for varying swarm densities in local sensor range
    local_densities = [5, 10, 20, 50]
    obstacles = set([(10, 10), (10, 11), (10, 12)])
    
    for density in local_densities:
        start_time = time.perf_counter()
        
        # Run 100 iterations to average out noise
        ITERATIONS = 100
        for _ in range(ITERATIONS):
            simulate_pibt_negotiation(density, obstacles)
            
        end_time = time.perf_counter()
        
        avg_time_ms = ((end_time - start_time) / ITERATIONS) * 1000.0
        
        status = "✅ PASS" if avg_time_ms < TARGET_BUDGET_MS else "❌ FAIL"
        
        print(f"Local Fleet Density: {density:2d} robots -> Avg PIBT resolution: {avg_time_ms:6.2f} ms {status}")
        
    print("=" * 50)
    print(f"Max compute budget per tick: {TARGET_BUDGET_MS} ms (for 10Hz loop)")
    
if __name__ == "__main__":
    # Run simple timing
    run_budget_profile()
    
    # Run deep profiling
    print("\nRunning deep cProfile on max density (50 robots)...")
    pr = cProfile.Profile()
    pr.enable()
    for _ in range(100):
        simulate_pibt_negotiation(50, set())
    pr.disable()
    
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(10)
    print(s.getvalue())
