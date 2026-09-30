import os
import sys
import time
import json
import threading
from typing import Dict, Callable

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
root_dir = os.path.dirname(parent_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from vyuha.samvaad.messages import TaskBid, TaskAward
from vyuha.samvaad.transport import TransportABC, InProcessTransport

class ContractNetInitiator:
    def __init__(self, transport: TransportABC, auction_duration: float = 0.5):
        self.transport = transport
        self.auction_duration = auction_duration
        self.active_auctions = {} # task_id -> { "bids": {robot_id: cost}, "timer": Timer, "callback": func }
        
        self.transport.subscribe("vyuha/auction/bid", self._on_bid_received)

    def _on_bid_received(self, topic: str, payload: bytes):
        print(f"[Initiator] RAW BID RECEIVED: {payload}")
        try:
            bid = TaskBid.model_validate_json(payload)
            if bid.task_id in self.active_auctions:
                self.active_auctions[bid.task_id]["bids"][bid.robot_id] = bid.cost
                print(f"[Initiator] Received bid {bid.cost:.1f} for task {bid.task_id} from {bid.robot_id}")
            else:
                print(f"[Initiator] Bid for unknown task: {bid.task_id}")
        except Exception as e:
            print(f"[Initiator] Error processing bid: {e}")

    def start_auction(self, task_id: str, on_complete: Callable[[str, str], None]):
        """Starts an auction for a task."""
        print(f"[Initiator] Starting auction for task {task_id}")
        
        def end_auction():
            auction_data = self.active_auctions.pop(task_id, None)
            if not auction_data:
                return
                
            bids = auction_data["bids"]
            if not bids:
                print(f"[Initiator] Auction for {task_id} failed: No bids received.")
                auction_data["callback"](task_id, None)
                return
                
            # Find lowest cost bid
            winner = min(bids.items(), key=lambda x: x[1])[0]
            print(f"[Initiator] Auction for {task_id} won by {winner} (cost: {bids[winner]:.1f})")
            
            # Broadcast award
            award = TaskAward(task_id=task_id, robot_id=winner)
            self.transport.publish("vyuha/auction/award", award.model_dump_json().encode('utf-8'))
            
            # Notify callback
            auction_data["callback"](task_id, winner)

        timer = threading.Timer(self.auction_duration, end_auction)
        self.active_auctions[task_id] = {"bids": {}, "timer": timer, "callback": on_complete}
        
        announcement = {"task_id": task_id, "timestamp": time.time()}
        self.transport.publish("vyuha/auction/announce", json.dumps(announcement).encode('utf-8'))
        
        timer.start()

class ContractNetParticipant:
    def __init__(self, robot_id: str, transport: TransportABC, bid_func: Callable[[str], float]):
        self.robot_id = robot_id
        self.transport = transport
        self.bid_func = bid_func
        
        self.transport.subscribe("vyuha/auction/announce", self._on_announce)
        self.transport.subscribe("vyuha/auction/award", self._on_award)
        
    def _on_announce(self, topic: str, payload: bytes):
        try:
            data = json.loads(payload.decode('utf-8'))
            task_id = data["task_id"]
            
            cost = self.bid_func(task_id)
            if cost < float('inf'):
                bid = TaskBid(robot_id=self.robot_id, task_id=task_id, cost=cost)
                print(f"[{self.robot_id}] Bidding {cost:.1f} for {task_id}")
                self.transport.publish("vyuha/auction/bid", bid.model_dump_json().encode('utf-8'))
        except Exception:
            pass

    def _on_award(self, topic: str, payload: bytes):
        try:
            award = TaskAward.model_validate_json(payload)
            if award.robot_id == self.robot_id:
                print(f"[{self.robot_id}] I won task {award.task_id}!")
        except Exception:
            pass

if __name__ == "__main__":
    print("Testing Contract Net Protocol...")
    
    transport = InProcessTransport()
    
    initiator = ContractNetInitiator(transport, auction_duration=0.2)
    
    def bid_r1(task_id): return 15.0 # AMR_1 is busy/far
    def bid_r2(task_id): return 5.0  # AMR_2 is close
    def bid_r3(task_id): return 25.0 # AMR_3 is very far
    
    r1 = ContractNetParticipant("AMR_1", transport, bid_r1)
    r2 = ContractNetParticipant("AMR_2", transport, bid_r2)
    r3 = ContractNetParticipant("AMR_3", transport, bid_r3)
    
    results = {}
    def on_auction_done(task_id, winner):
        results[task_id] = winner
        
    initiator.start_auction("T_001", on_auction_done)
    
    # Wait for auction to complete
    time.sleep(0.5)
    
    assert results.get("T_001") == "AMR_2", "AMR_2 should have won the auction due to lowest bid"
    print("SUCCESS: Contract Net Protocol verified.")
    transport.close()
