from pydantic import BaseModel, Field
from typing import List
import time

class BeliefState(BaseModel):
    robot_id: str
    x: float
    y: float
    theta: float
    battery: float = Field(ge=0, le=100)
    timestamp: float = Field(default_factory=time.time)

class TaskBid(BaseModel):
    robot_id: str
    task_id: str
    cost: float = Field(ge=0)
    timestamp: float = Field(default_factory=time.time)

class TaskAward(BaseModel):
    task_id: str
    robot_id: str
    timestamp: float = Field(default_factory=time.time)

class ConflictWarning(BaseModel):
    robot_ids: List[str]
    x: float
    y: float
    time_tick: int
    timestamp: float = Field(default_factory=time.time)

if __name__ == "__main__":
    print("Testing Pydantic Message Schemas...")
    
    # 1. BeliefState
    bs = BeliefState(robot_id="AMR_1", x=10.5, y=2.0, theta=1.57, battery=98.0)
    print(f"BeliefState valid: {bs.model_dump_json()}")
    
    # 2. TaskBid
    bid = TaskBid(robot_id="AMR_1", task_id="T_001", cost=15.5)
    print(f"TaskBid valid: {bid.model_dump_json()}")
    
    # 3. TaskAward
    award = TaskAward(task_id="T_001", robot_id="AMR_1")
    print(f"TaskAward valid: {award.model_dump_json()}")
    
    # 4. ConflictWarning
    conflict = ConflictWarning(robot_ids=["AMR_1", "AMR_2"], x=7.0, y=4.0, time_tick=5)
    print(f"ConflictWarning valid: {conflict.model_dump_json()}")
    
    # Test Validation failure
    try:
        invalid_bs = BeliefState(robot_id="AMR_1", x=0, y=0, theta=0, battery=150.0)
        assert False, "Validation should have failed for battery > 100"
    except ValueError as e:
        print("Validation correctly rejected invalid battery (>100)")
        
    print("SUCCESS: Pydantic schemas for SAMVAAD messages validated.")
