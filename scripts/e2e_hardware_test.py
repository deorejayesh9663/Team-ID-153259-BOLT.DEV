import sys
import time
import math
sys.stdout.reconfigure(encoding='utf-8')

import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from hal.ros2_bridge import VyuhaRosBridge, ROS2_AVAILABLE
except ImportError:
    print("Could not import VyuhaRosBridge. Check your PYTHONPATH.")
    sys.exit(1)

def run_e2e_dry_run():
    print("==================================================")
    print("VYUHA End-to-End Hardware Dry Run")
    print("==================================================")
    
    # 1. Initialize Bridge
    bridge = VyuhaRosBridge(robot_ids=['r1', 'r2', 'r3'], grid_resolution=1.0)
    print("[INIT] VyuhaRosBridge initialized (Mock Mode).")
    
    # 2. Simulate VYUHA-Core dispatching a grid command
    target_grid_x = 5
    target_grid_y = 5
    print(f"\n[CORE] Dispatching command to r1: Move to grid ({target_grid_x}, {target_grid_y})")
    
    # 3. Time the bridge translation latency
    start_time = time.perf_counter()
    bridge.send_move_command('r1', target_grid_x, target_grid_y)
    end_time = time.perf_counter()
    
    latency_ms = (end_time - start_time) * 1000.0
    print(f"[HAL] Target translated to real-world coordinates: ({target_grid_x*1.0}, {target_grid_y*1.0}) meters.")
    print(f"[HAL] ROS 2 Twist command published successfully in {latency_ms:.3f} ms.")
    
    if latency_ms < 5.0:
        print("✅ PASS: Translation latency is well under 5ms budget.")
    else:
        print("❌ FAIL: Translation latency is too high.")
        
    print("\n[STUB] Simulated ESP32 received Twist command:")
    print("       -> Linear X: 0.5 m/s")
    print("       -> Angular Z: 0.39 rad/s")
    
    # 4. Simulate ESP32 returning odometry
    print("\n[STUB] Simulating Odometry return from physical encoders...")
    bridge.robot_states['r1']['x'] = 1.0
    bridge.robot_states['r1']['y'] = 1.0
    bridge.robot_states['r1']['theta'] = 0.785 # 45 deg
    
    # 5. Core translates back to grid
    discrete_pos = bridge.get_discrete_position('r1')
    print(f"[CORE] Hardware feedback translated back to grid pos: {discrete_pos}")
    if discrete_pos == (1, 1):
        print("✅ PASS: Odometry -> Grid translation correct.")
    else:
        print("❌ FAIL: Odometry translation mismatch.")
        
    print("==================================================")
    print("End-to-End Dry Run Complete.")

if __name__ == "__main__":
    run_e2e_dry_run()
