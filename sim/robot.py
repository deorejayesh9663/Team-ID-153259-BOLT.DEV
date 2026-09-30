import math
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from planner import AStarPlanner

class Robot:
    def __init__(self, robot_id, x, y):
        self.robot_id = robot_id
        self.x = float(x)
        self.y = float(y)
        self.task = None
        self.path = []
        self.speed = 2.0 # cells per second
        
    def assign_task(self, task, planner: AStarPlanner):
        self.task = task
        self.task.state = "IN_PROGRESS_PICK"
        self.path = planner.plan((int(round(self.x)), int(round(self.y))), self.task.pick_node)
        if self.path and self.path[0] == (int(round(self.x)), int(round(self.y))):
            self.path.pop(0)

    def tick(self, dt, planner: AStarPlanner):
        if not self.task:
            return

        if self.path:
            target_x, target_y = self.path[0]
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)
            
            step = self.speed * dt
            if step >= dist:
                self.x, self.y = float(target_x), float(target_y)
                self.path.pop(0)
            else:
                self.x += (dx / dist) * step
                self.y += (dy / dist) * step
                
        else:
            if self.task.state == "IN_PROGRESS_PICK":
                print(f"[{self.robot_id}] Reached pick node {self.task.pick_node}. Picking up item...")
                self.task.state = "IN_PROGRESS_DROP"
                self.path = planner.plan((int(round(self.x)), int(round(self.y))), self.task.drop_node)
                if self.path and self.path[0] == (int(round(self.x)), int(round(self.y))):
                    self.path.pop(0)
            elif self.task.state == "IN_PROGRESS_DROP":
                print(f"[{self.robot_id}] Reached drop node {self.task.drop_node}. Task Complete.")
                self.task.state = "COMPLETED"
                self.task = None
