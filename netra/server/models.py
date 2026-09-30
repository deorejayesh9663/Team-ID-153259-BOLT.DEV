from enum import Enum
from pydantic import BaseModel, Field
import time
from typing import Optional

class TaskState(str, Enum):
    UNASSIGNED = "UNASSIGNED"
    BIDDING = "BIDDING"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class JobTask(BaseModel):
    task_id: str
    target_x: float
    target_y: float
    state: TaskState = TaskState.UNASSIGNED
    assigned_to: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    
    def transition(self, new_state: TaskState, robot_id: Optional[str] = None):
        valid_transitions = {
            TaskState.UNASSIGNED: [TaskState.BIDDING],
            TaskState.BIDDING: [TaskState.ASSIGNED, TaskState.UNASSIGNED],
            TaskState.ASSIGNED: [TaskState.IN_PROGRESS, TaskState.UNASSIGNED],
            TaskState.IN_PROGRESS: [TaskState.COMPLETED, TaskState.UNASSIGNED],
            TaskState.COMPLETED: []
        }
        
        if new_state not in valid_transitions[self.state]:
            raise ValueError(f"Invalid transition from {self.state.name} to {new_state.name}")
            
        if new_state == TaskState.ASSIGNED and not robot_id:
            raise ValueError("Must provide robot_id when transitioning to ASSIGNED")
            
        if new_state == TaskState.UNASSIGNED:
            self.assigned_to = None
        elif robot_id:
            self.assigned_to = robot_id
            
        self.state = new_state

if __name__ == "__main__":
    print("Testing JobTask model...")
    t = JobTask(task_id="T1", target_x=10.0, target_y=5.0)
    print(f"Created task: {t.task_id} in state {t.state}")
    
    t.transition(TaskState.BIDDING)
    print(f"Transitioned to {t.state}")
    
    t.transition(TaskState.ASSIGNED, robot_id="AMR_1")
    print(f"Assigned to {t.assigned_to}. State: {t.state}")
    
    t.transition(TaskState.IN_PROGRESS)
    print(f"Transitioned to {t.state}")
    
    t.transition(TaskState.COMPLETED)
    print(f"Transitioned to {t.state}")
    
    try:
        t.transition(TaskState.UNASSIGNED)
        assert False, "Should not be able to transition from COMPLETED"
    except ValueError as e:
        print(f"Caught expected error: {e}")
        
    print("SUCCESS: Task models and lifecycle verified.")
