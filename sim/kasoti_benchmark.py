import os
import sys
import time
import random
import numpy as np

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from baseline.hungarian import assign_tasks_hungarian
from vyuha.samvaad.deadlock import PIBTRunner
from vyuha.core.bidding import calculate_bid
from vyuha_core.planning.dstar_lite import DStarLite

try:
    import onnxruntime as ort
except ImportError:
    ort = None

class KasotiBenchmark:
    def __init__(self, mode="BASELINE", num_robots=50, num_tasks=200, grid_size=20):
        self.mode = mode
        self.num_robots = num_robots
        self.num_tasks = num_tasks
        self.grid_size = grid_size
        
        self.robots = {} # r_id -> {"pos": (x,y), "target": None, "priority": id_num}
        self.tasks_pending = [] # list of (x,y)
        self.tasks_completed = 0
        
        self.obstacles = set()
        self.wifi_dead_zones = [] # List of dicts with x_min, x_max, y_min, y_max
        self.blackout = False
        self.human_actor = None
        self.packet_loss_active = False
        self.express_robot = None
        self.active_planner = "D* LITE"
        self.ai_advisor_active = True
        self.planner = DStarLite(grid_size=self.grid_size)
        
        self.deadlocks = 0
        self.ticks = 0
        
        if self.mode == "VYUHA+AI" and ort is not None:
            models_dir = os.path.join(parent_dir, "models")
            self.ort_priority = ort.InferenceSession(os.path.join(models_dir, "priority_tree.onnx"))
            self.ort_congestion = ort.InferenceSession(os.path.join(models_dir, "congestion_gru.onnx"))
        
    def setup(self, seed=42):
        random.seed(seed)
        np.random.seed(seed)
        
        # Ensure unique starting positions
        all_cells = [(x, y) for x in range(self.grid_size) for y in range(self.grid_size)]
        robot_starts = random.sample(all_cells, self.num_robots)
        
        for i in range(self.num_robots):
            if self.mode == "VYUHA+AI" and ort is not None:
                payload = random.uniform(0.0, 100.0)
                deadline = random.uniform(0.0, 1.0)
                input_data = np.array([[payload, deadline]], dtype=np.float32)
                priority_pred = self.ort_priority.run(None, {'float_input': input_data})[0][0]
                base_priority = int(priority_pred)
                # Map 1-5 (1 is best) to PIBT where higher integer = higher priority.
                # Use i as tie-breaker to prevent identical priorities causing cyclic deadlocks.
                pibt_priority = (6 - base_priority) * 1000 + i
            else:
                pibt_priority = i
            self.robots[f"AMR_{i}"] = {"pos": robot_starts[i], "target": None, "priority": pibt_priority}
            
        for _ in range(self.num_tasks):
            tx = random.randint(0, self.grid_size - 1)
            ty = random.randint(0, self.grid_size - 1)
            self.tasks_pending.append((tx, ty))
            
    def _get_manhattan_moves(self, pos, target):
        x, y = pos
        tx, ty = target
        moves = []
        if x < tx: moves.append((x+1, y))
        elif x > tx: moves.append((x-1, y))
        
        if y < ty: moves.append((x, y+1))
        elif y > ty: moves.append((x, y-1))
        return moves

    def run(self):
        print(f"Starting {self.mode} benchmark (Robots: {self.num_robots}, Tasks: {self.num_tasks})...")
        start_time = time.time()
        
    def _in_dead_zone(self, pos):
        x, y = pos
        for dz in self.wifi_dead_zones:
            if dz['x_min'] <= x <= dz['x_max'] and dz['y_min'] <= y <= dz['y_max']:
                return True
        return False

    def step(self):
        self.ticks += 1
        
        # --- CHAOS SCENARIO C3: Blocked Aisle ---
        if self.ticks == 20:
            print("[CHAOS] C3 triggered: Dynamic obstacle blocking aisle at x=15.")
            new_obstacles = set((15, y) for y in range(10, 20))
            self.obstacles.update(new_obstacles)
            self.planner.update_obstacles(self.obstacles)
            
        # --- CHAOS SCENARIO C4: Wi-Fi Dead Zone ---
        if self.ticks == 40:
            print("[CHAOS] C4 triggered: Wi-Fi Dead Zone at top-right quadrant.")
            self.wifi_dead_zones.append({
                'x_min': 20, 'x_max': 29,
                'y_min': 0, 'y_max': 9
            })
            
        # --- CHAOS SCENARIO C5: Total Blackout ---
        if self.ticks == 60:
            print("[CHAOS] C5 triggered: TOTAL BLACKOUT. Safe-mode engaged.")
            self.blackout = True
        elif self.ticks == 80:
            print("[CHAOS] C5 resolved: Blackout lifted. Commencing recovery.")
            self.blackout = False
            
        # --- CHAOS SCENARIO C8: Human Actor ---
        if self.ticks == 100:
            print("[CHAOS] C8 triggered: Human actor spawned at (15,15).")
            self.human_actor = {"pos": (15, 15)}
            
        if self.human_actor:
            # Remove old position from obstacles
            old_pos = self.human_actor["pos"]
            if old_pos in self.obstacles:
                self.obstacles.remove(old_pos)
            
            # Random walk
            x, y = old_pos
            possible_moves = [(x+1, y), (x-1, y), (x, y+1), (x, y-1), (x, y)]
            valid_moves = [m for m in possible_moves if 0 <= m[0] < self.grid_size and 0 <= m[1] < self.grid_size]
            new_pos = random.choice(valid_moves)
            
            self.human_actor["pos"] = new_pos
            self.obstacles.add(new_pos)
            self.planner.update_obstacles(self.obstacles)
            
        # --- CHAOS SCENARIO C11: 30% Packet Loss ---
        if self.ticks == 200:
            print("[CHAOS] C11 triggered: 30% SAMVAAD packet loss rate active.")
            self.packet_loss_active = True
        elif self.ticks == 250:
            print("[CHAOS] C11 resolved: Network stabilized.")
            self.packet_loss_active = False
            
        # --- CHAOS SCENARIO C9: Choke-Point Storm ---
        if self.ticks == 150:
            print("[CHAOS] C9 triggered: Choke-Point Storm at (20, 20).")
            # Select first 8 robots
            storm_robots = list(self.robots.keys())[:8]
            formation = [
                {"pos": (20, 16), "target": (20, 24)}, # N -> S
                {"pos": (20, 24), "target": (20, 16)}, # S -> N
                {"pos": (16, 20), "target": (24, 20)}, # W -> E
                {"pos": (24, 20), "target": (16, 20)}, # E -> W
                {"pos": (18, 18), "target": (22, 22)}, # NW -> SE
                {"pos": (22, 18), "target": (18, 22)}, # NE -> SW
                {"pos": (18, 22), "target": (22, 18)}, # SW -> NE
                {"pos": (22, 22), "target": (18, 18)}  # SE -> NW
            ]
            
            for i, r_id in enumerate(storm_robots):
                # Remove their old targets from pending if needed (simplification: just drop them)
                self.robots[r_id]["pos"] = formation[i]["pos"]
                self.robots[r_id]["target"] = formation[i]["target"]
                self.robots[r_id]["priority"] = 1000 + i # High priority to force interaction
                
        # --- CHAOS SCENARIO C12: EXPRESS Priority Pre-emption ---
        if self.ticks == 250:
            self.express_robot = list(self.robots.keys())[0]
            print(f"[CHAOS] C12 triggered: EXPRESS VIP assigned to {self.express_robot}.")
            self.robots[self.express_robot]["pos"] = (5, 5)
            self.robots[self.express_robot]["target"] = (38, 38)
            
        # --- CHAOS SCENARIO C13: Live A/B Toggle ---
        if self.ticks == 300:
            print("[CHAOS] C13 triggered: Swapping planner to A* FALLBACK.")
            self.active_planner = "A* FALLBACK"
        elif self.ticks == 350:
            print("[CHAOS] C13 resolved: Restoring D* LITE.")
            self.active_planner = "D* LITE"
            
        # --- CHAOS SCENARIO C14: Live AI-advisor OFF Toggle ---
        if self.ticks == 400:
            print("[CHAOS] C14 triggered: Cloud partition. AI Advisor OFFLINE.")
            self.ai_advisor_active = False
            
        for r_id in self.robots:
            if not (self.ticks >= 150 and self.ticks < 250 and r_id in list(self.robots.keys())[:8]):
                if r_id != self.express_robot or self.ticks < 250 or self.ticks > 350:
                    self.robots[r_id]["intent"] = None
        
        # 1. Assignment Phase
        # Exclude robots in Wi-Fi dead zones from receiving new assignments
        idle_robots = {r_id: r_data["pos"] for r_id, r_data in self.robots.items() 
                       if not r_data["target"] and not self._in_dead_zone(r_data["pos"])}
        
        if idle_robots and self.tasks_pending and not self.blackout:
            num_to_assign = min(len(idle_robots), len(self.tasks_pending))
            tasks_to_assign = {f"T_{i}": self.tasks_pending[i] for i in range(num_to_assign)}
            
            if self.mode == "BASELINE":
                # Global Hungarian assignment
                assignments = assign_tasks_hungarian(idle_robots, tasks_to_assign)
                for t_id, r_id in assignments.items():
                    self.robots[r_id]["target"] = tasks_to_assign[t_id]
                    self.robots[r_id]["intent"] = "Assigned"
                    self.tasks_pending.remove(tasks_to_assign[t_id])
            else:
                # VYUHA CNP (Distributed Greedy Bidding)
                for t_id, t_pos in tasks_to_assign.items():
                    best_r = None
                    best_bid = float('inf')
                    for r_id in idle_robots.keys():
                        if not self.robots[r_id]["target"]:
                            base_bid = calculate_bid(self.robots[r_id]["pos"], t_pos, 100.0)
                            
                            if self.mode == "VYUHA+AI" and ort is not None:
                                seq = np.random.uniform(0, 0.5, size=(1, 5, 1)).astype(np.float32)
                                wait_time_pred = self.ort_congestion.run(None, {'input': seq})[0][0][0]
                                adjusted_bid = base_bid + float(wait_time_pred)
                            else:
                                adjusted_bid = base_bid
                                
                            if adjusted_bid < best_bid:
                                best_bid = adjusted_bid
                                best_r = r_id
                    if best_r:
                        self.robots[best_r]["target"] = t_pos
                        self.robots[best_r]["intent"] = f"Bid: {best_bid:.1f}"
                        self.tasks_pending.remove(t_pos)

        # 2. Movement Phase
        if self.blackout:
            for r_id in self.robots:
                # In a total blackout, robots drop their tasks and enter safe mode
                if self.robots[r_id]["target"]:
                    self.tasks_pending.append(self.robots[r_id]["target"])
                    self.robots[r_id]["target"] = None
                self.robots[r_id]["intent"] = "SAFE MODE"

        moving_agents = {r_id: r_data for r_id, r_data in self.robots.items() if r_data["target"]}
        
        if self.mode == "BASELINE":
            proposed_moves = {}
            for r_id, data in moving_agents.items():
                moves = self._get_manhattan_moves(data["pos"], data["target"])
                proposed_moves[r_id] = moves[0] if moves else data["pos"]
                
            all_positions = {data["pos"] for data in self.robots.values()}
            for r_id, next_pos in proposed_moves.items():
                current_pos = moving_agents[r_id]["pos"]
                all_other_positions = all_positions - {current_pos}
                
                if next_pos in all_other_positions:
                    self.deadlocks += 1
                    self.robots[r_id]["intent"] = "Waiting"
                else:
                    self.robots[r_id]["pos"] = next_pos
                    all_positions.remove(current_pos)
                    all_positions.add(next_pos)
                    
        else:
            pibt_agents = {}
            for r_id, r_data in self.robots.items():
                if r_data["target"]:
                    if self.ai_advisor_active:
                        # Cloud AI (D* Lite) computes optimal path
                        immediate_target = self.planner.get_next_move(r_data["pos"], r_data["target"])
                    else:
                        # Fallback to naive greedy routing (no global obstacle awareness)
                        cx, cy = r_data["pos"]
                        tx, ty = r_data["target"]
                        if cx < tx: immediate_target = (cx + 1, cy)
                        elif cx > tx: immediate_target = (cx - 1, cy)
                        elif cy < ty: immediate_target = (cx, cy + 1)
                        elif cy > ty: immediate_target = (cx, cy - 1)
                        else: immediate_target = (cx, cy)
                        self.robots[r_id]["intent"] = "AI OFFLINE"
                else:
                    immediate_target = r_data["pos"]
                    
                # Apply Wi-Fi dead zone degradation
                current_priority = r_data["priority"]
                if self._in_dead_zone(r_data["pos"]):
                    current_priority = -1 # Loss of SAMVAAD gossip; defaults to lowest priority
                    self.robots[r_id]["intent"] = "LiDAR Fallback"
                    
                # Apply 30% Packet Loss
                elif self.packet_loss_active and random.random() < 0.3:
                    current_priority = -1
                    self.robots[r_id]["intent"] = "PACKET LOSS"
                    
                if self.ticks >= 150 and self.ticks < 250 and r_id in list(self.robots.keys())[:8]:
                    self.robots[r_id]["intent"] = "CHOKE STORM"
                    
                if self.ticks >= 250 and self.ticks < 350 and r_id == self.express_robot:
                    current_priority = 9999
                    self.robots[r_id]["intent"] = "EXPRESS VIP"
                    
                pibt_agents[r_id] = {"pos": r_data["pos"], "target": immediate_target, "priority": current_priority}
                
            def get_valid_moves(pos):
                x, y = pos
                raw_moves = [(x+1, y), (x-1, y), (x, y+1), (x, y-1), (x, y)]
                return [m for m in raw_moves if 0 <= m[0] < self.grid_size and 0 <= m[1] < self.grid_size and m not in self.obstacles]
                
            pibt = PIBTRunner(pibt_agents, get_valid_moves)
            next_positions = pibt.run()
            
            for r_id, next_pos in next_positions.items():
                wanted_moves = self._get_manhattan_moves(self.robots[r_id]["pos"], self.robots[r_id]["target"]) if self.robots[r_id]["target"] else []
                if wanted_moves and next_pos not in wanted_moves:
                    self.deadlocks += 1 
                    self.robots[r_id]["intent"] = "Yielding"
                
                self.robots[r_id]["pos"] = next_pos
                
        # 3. Completion Check
        for r_id, data in self.robots.items():
            if data["target"] and data["pos"] == data["target"]:
                data["target"] = None
                data["intent"] = "Task Complete"
                self.tasks_completed += 1

    def run(self):
        print(f"Starting {self.mode} benchmark (Robots: {self.num_robots}, Tasks: {self.num_tasks})...")
        start_time = time.time()
        
        while self.tasks_completed < self.num_tasks and self.ticks < 3000:
            self.step()
        
        elapsed = time.time() - start_time
        
        if self.ticks >= 3000:
            print(f"[{self.mode}] FAILED: Exceeded 3000 ticks. Permanent Gridlock. Completed {self.tasks_completed}/{self.num_tasks} tasks.")
            success = False
        else:
            print(f"[{self.mode}] SUCCESS: Completed {self.tasks_completed} tasks in {self.ticks} ticks ({elapsed:.2f}s).")
            success = True
            
        return {
            "mode": self.mode,
            "success": success,
            "ticks": self.ticks,
            "tasks": self.tasks_completed,
            "deadlock_events": self.deadlocks
        }

if __name__ == "__main__":
    print("=== KASOTI BENCHMARK RUNNER ===")
    
    # Run Baseline
    baseline = KasotiBenchmark(mode="BASELINE", num_robots=20, num_tasks=100, grid_size=30)
    baseline.setup(seed=104)
    res_b = baseline.run()
    
    # Run VYUHA
    vyuha = KasotiBenchmark(mode="VYUHA", num_robots=20, num_tasks=100, grid_size=30)
    vyuha.setup(seed=104)
    res_v = vyuha.run()
    
    # Run VYUHA+AI
    vyuha_ai = KasotiBenchmark(mode="VYUHA+AI", num_robots=20, num_tasks=100, grid_size=30)
    vyuha_ai.setup(seed=104)
    res_v_ai = vyuha_ai.run()
    
    print("\n--- RESULTS ---")
    print(f"BASELINE: Success={res_b['success']}, Tasks={res_b['tasks']}, Ticks={res_b['ticks']}, Resolvable Deadlocks/Stops={res_b['deadlock_events']}")
    print(f"VYUHA   : Success={res_v['success']}, Tasks={res_v['tasks']}, Ticks={res_v['ticks']}, PIBT Yields={res_v['deadlock_events']}")
    print(f"VYUHA+AI: Success={res_v_ai['success']}, Tasks={res_v_ai['tasks']}, Ticks={res_v_ai['ticks']}, PIBT Yields={res_v_ai['deadlock_events']}")
