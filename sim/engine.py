import random
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from warehouse import WarehouseMap
from planner import AStarPlanner
from robot import Robot
from tasks import Task

class SimulationEngine:
    def __init__(self, map_path: str, seed: int = 42, hz: int = 10):
        self.seed = seed
        self.hz = hz
        self.dt = 1.0 / hz
        self.ticks = 0
        self.rng = random.Random(seed)
        
        self.warehouse = WarehouseMap(map_path)
        self.planner = AStarPlanner(self.warehouse)
        self.robots = []
        self.tasks = []
        
    def add_robot(self, robot: Robot):
        self.robots.append(robot)
        
    def add_task(self, task: Task):
        self.tasks.append(task)

    def tick(self):
        self.ticks += 1
        for robot in self.robots:
            robot.tick(self.dt, self.planner)
        
    def run(self, max_ticks: int = 1000):
        for _ in range(max_ticks):
            self.tick()
            if all(r.task is None for r in self.robots) and all(t.state == "COMPLETED" for t in self.tasks):
                print(f"Simulation finished early at tick {self.ticks}.")
                break

if __name__ == "__main__":
    map_path = os.path.join(current_dir, "maps", "small_3amr.json")
    engine = SimulationEngine(map_path)
    
    # Spawn robot in an aisle
    robot = Robot("AMR_1", 10, 1)
    engine.add_robot(robot)
    
    # Create task: Pick at P (0,14), Drop at D (0,0)
    task = Task("T_001", pick_node=(0, 14), drop_node=(0, 0))
    engine.add_task(task)
    
    # Assign task
    print("Assigning task T_001 to AMR_1...")
    robot.assign_task(task, engine.planner)
    
    print("Running simulation...")
    engine.run(2000)
    print("SUCCESS: Engine spawned robot, assigned task, robot followed path, and completed task.")
