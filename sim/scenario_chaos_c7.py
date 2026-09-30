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
from vyuha.core.battery import BatteryManager

if __name__ == "__main__":
    print("Testing Chaos C7: Battery brownout re-assignment...")
    
    transport = InProcessTransport()
    
    task = JobTask(task_id="T_HEAVY", target_x=100, target_y=100)
    
    def on_auction_done(task_id, winner):
        if winner:
            task.transition(TaskState.ASSIGNED, winner)
            print(f"[Dispatcher] {task_id} assigned to {winner}")
        else:
            task.transition(TaskState.UNASSIGNED)
            print(f"[Dispatcher] {task_id} unassigned")

    initiator_r1 = ContractNetInitiator(transport, auction_duration=0.2)
    initiator_dispatcher = ContractNetInitiator(transport, auction_duration=0.2)
    
    def bid_r2(t_id): return 50.0 # R2 is healthy but further away
    r2 = ContractNetParticipant("AMR_2", transport, bid_r2)
    
    print("[Sim] Dispatcher starting auction...")
    task.transition(TaskState.BIDDING)
    
    def bid_r1(t_id): return 10.0
    r1 = ContractNetParticipant("AMR_1", transport, bid_r1)
    
    initiator_dispatcher.start_auction(task.task_id, on_auction_done)
    time.sleep(0.3)
    
    assert task.assigned_to == "AMR_1"
    
    print("[Sim] AMR_1 begins long journey...")
    task.transition(TaskState.IN_PROGRESS)
    
    bm = BatteryManager(charge=22.0, discharge_rate_moving=5.0)
    
    bm.tick(0.5, is_moving=True)
    print(f"[AMR_1] Moving... Battery: {bm.charge:.1f}%")
    
    bm.tick(0.5, is_moving=True)
    print(f"[AMR_1] Moving... Battery: {bm.charge:.1f}%")
    
    if bm.needs_charging():
        print("[AMR_1] WARNING: BROWNOUT! Battery < 20%!")
        print("[AMR_1] Abandoning task T_HEAVY and re-auctioning to peers!")
        
        r1.bid_func = lambda t: float('inf')
        
        task.transition(TaskState.UNASSIGNED)
        task.transition(TaskState.BIDDING)
        
        initiator_r1.start_auction(task.task_id, on_auction_done)
        
        docks = [(0, 0), (50, 50)]
        nearest = bm.get_nearest_dock((10, 10), docks)
        print(f"[AMR_1] Routing to emergency dock at {nearest}...")
        
    time.sleep(0.3)
    
    assert task.assigned_to == "AMR_2", f"Expected AMR_2 to recover task, got {task.assigned_to}"
    print("[Sim] SUCCESS: AMR_1 autonomously abandoned the task and AMR_2 recovered it!")
