import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
root_dir = os.path.dirname(parent_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from vyuha.samvaad.transport import InProcessTransport
from vyuha.core.auction import ContractNetInitiator, ContractNetParticipant
from netra.server.models import JobTask, TaskState

if __name__ == "__main__":
    print("Testing Chaos C6: Robot dies mid-task, re-auctioned...")
    
    transport = InProcessTransport()
    initiator = ContractNetInitiator(transport, auction_duration=0.2)
    
    task = JobTask(task_id="T_002", target_x=10, target_y=10)
    
    # Robots
    def bid_r1(t_id): return 5.0  # R1 will win initially
    def bid_r2(t_id): return 15.0 # R2 will win after R1 dies
    
    r1 = ContractNetParticipant("AMR_1", transport, bid_r1)
    r2 = ContractNetParticipant("AMR_2", transport, bid_r2)
    
    robot_health = {"AMR_1": True, "AMR_2": True}
    
    def on_auction_done(task_id, winner):
        if winner:
            task.transition(TaskState.ASSIGNED, winner)
            print(f"[Dispatcher] {task_id} assigned to {winner}")
        else:
            print(f"[Dispatcher] {task_id} unassigned")
            task.transition(TaskState.UNASSIGNED)
            
    print("[Sim] Initiating first auction...")
    task.transition(TaskState.BIDDING)
    initiator.start_auction(task.task_id, on_auction_done)
    
    time.sleep(0.3)
    
    assert task.assigned_to == "AMR_1", f"Task should be assigned to AMR_1, got {task.assigned_to}"
    
    print("[Sim] AMR_1 begins task...")
    task.transition(TaskState.IN_PROGRESS)
    
    print("[Sim] *BZZT* AMR_1 hardware failure! Dying mid-task...")
    robot_health["AMR_1"] = False
    
    # A background monitor detects the failure
    def monitor_fleet():
        if task.state == TaskState.IN_PROGRESS and task.assigned_to:
            if not robot_health.get(task.assigned_to, False):
                print(f"[Monitor] Detected {task.assigned_to} offline! Re-assigning task {task.task_id}...")
                task.transition(TaskState.UNASSIGNED)
                task.transition(TaskState.BIDDING)
                
                # Kill R1's participant so it doesn't bid again
                r1.bid_func = lambda t: float('inf')
                
                initiator.start_auction(task.task_id, on_auction_done)

    monitor_fleet()
    time.sleep(0.3)
    
    assert task.assigned_to == "AMR_2", f"Expected AMR_2 to recover task, got {task.assigned_to}"
    print("[Sim] SUCCESS: Task was successfully re-auctioned and recovered by AMR_2")
