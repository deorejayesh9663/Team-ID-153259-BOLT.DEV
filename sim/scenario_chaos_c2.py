import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from vyuha.samvaad.deadlock import PIBTRunner

if __name__ == "__main__":
    print("Testing Chaos C2: 4-Way Junction Deadlock with PIBT...")
    
    # 2x2 Roundabout Deadlock
    # 4 robots in a cycle wanting to move clockwise
    # (1,2) [AMR_4]  -> (2,2) [AMR_3]
    #   ^                  v
    # (1,1) [AMR_1]  <- (2,1) [AMR_2]
    
    # Priorities: 10, 9, 8, 7 (AMR_1 is highest)
    agents = {
        "AMR_1": {"pos": (1, 1), "target": (1, 2), "priority": 10},
        "AMR_2": {"pos": (2, 1), "target": (1, 1), "priority": 9},
        "AMR_3": {"pos": (2, 2), "target": (2, 1), "priority": 8},
        "AMR_4": {"pos": (1, 2), "target": (2, 2), "priority": 7}
    }
    
    def get_valid_moves(pos):
        x, y = pos
        # Cross topology to allow them to escape the roundabout
        moves = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        return moves
        
    pibt = PIBTRunner(agents, get_valid_moves)
    result = pibt.run()
    
    for agent_id, next_pos in result.items():
        print(f"[{agent_id}] Assigned to {next_pos}")
        
    # Validation
    # Because AMR_1 is highest priority, it will force the others to move.
    # The cycle breaks when the lowest agent in the cascade realizes it can't push the head of the chain.
    # Someone will have to yield outside the 2x2 box.
    assert result["AMR_1"] == (1, 2), "AMR_1 (highest priority) should successfully move to its target."
    
    # At least one robot should have moved OUTSIDE the 2x2 box to break the cycle.
    box = [(1,1), (1,2), (2,1), (2,2)]
    escaped = [r for r, pos in result.items() if pos not in box]
    
    assert len(escaped) > 0, "At least one robot must yield outside the roundabout to break the deadlock."
    
    print(f"SUCCESS: Deadlock broken! Robots that yielded outside the junction: {escaped}")
    print("Chaos C2 fully resolved via PIBT.")
