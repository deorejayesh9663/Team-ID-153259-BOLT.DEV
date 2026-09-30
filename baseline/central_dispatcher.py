import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
root_dir = os.path.dirname(parent_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from netra.server.models import JobTask, TaskState

class CentralDispatcher:
    """
    A single-point-of-failure (SPOF) dispatcher.
    Hard-assigns tasks based on simple distance, completely bypassing CNP.
    Does not leverage peer-to-peer bidding.
    """
    def __init__(self):
        self.robots = {} # robot_id -> {"pos": (x,y), "status": "IDLE"}
        self.tasks = {}
        
    def register_robot(self, robot_id: str, initial_pos: tuple):
        self.robots[robot_id] = {"pos": initial_pos, "status": "IDLE"}
        
    def add_task(self, task_id: str, target_pos: tuple):
        task = JobTask(task_id=task_id, target_x=target_pos[0], target_y=target_pos[1])
        self.tasks[task_id] = task
        self._dispatch()
        
    def _dispatch(self):
        for t_id, t in self.tasks.items():
            if t.state == TaskState.UNASSIGNED:
                # Find closest IDLE robot
                best_robot = None
                best_dist = float('inf')
                
                for r_id, r_data in self.robots.items():
                    if r_data["status"] == "IDLE":
                        dist = abs(r_data["pos"][0] - t.target_x) + abs(r_data["pos"][1] - t.target_y)
                        if dist < best_dist:
                            best_dist = dist
                            best_robot = r_id
                            
                if best_robot:
                    # Hard assign (skip bidding)
                    t.transition(TaskState.BIDDING)
                    t.transition(TaskState.ASSIGNED, best_robot)
                    self.robots[best_robot]["status"] = "BUSY"
                    print(f"[CentralDispatcher] Hard-assigned {t_id} to {best_robot}")

if __name__ == "__main__":
    print("Testing Central Dispatcher (Baseline SPOF)...")
    dispatcher = CentralDispatcher()
    
    dispatcher.register_robot("AMR_1", (0, 0))
    dispatcher.register_robot("AMR_2", (10, 10))
    
    dispatcher.add_task("T_001", (1, 1))
    dispatcher.add_task("T_002", (9, 9))
    
    assert dispatcher.tasks["T_001"].assigned_to == "AMR_1"
    assert dispatcher.tasks["T_002"].assigned_to == "AMR_2"
    
    print("SUCCESS: Centralized assignment verified.")
