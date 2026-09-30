def calculate_bid(robot_pos: tuple, task_pos: tuple, battery: float) -> float:
    """
    Calculates the bid cost for a robot to take a task.
    Lower cost = better bid.
    Cost is primarily the Manhattan distance to the task.
    If battery is below 30%, a steep penalty is added to discourage assignment unless necessary.
    Returns float('inf') if battery is <= 0.
    """
    if battery <= 0:
        return float('inf')
        
    rx, ry = robot_pos
    tx, ty = task_pos
    
    distance = abs(rx - tx) + abs(ry - ty)
    
    penalty = 0.0
    if battery < 30.0:
        # Scale penalty up as battery goes down
        penalty = 100.0 * (30.0 - battery)
        
    return float(distance + penalty)

if __name__ == "__main__":
    print("Testing calculate_bid...")
    
    # Healthy robot near task
    cost1 = calculate_bid((0,0), (1,1), 90.0)
    assert cost1 == 2.0
    
    # Healthy robot far from task
    cost2 = calculate_bid((0,0), (10,10), 90.0)
    assert cost2 == 20.0
    
    # Low battery robot near task
    cost3 = calculate_bid((0,0), (1,1), 20.0)
    # distance = 2, penalty = 100 * (10) = 1000
    assert cost3 == 1002.0
    
    # Dead robot
    cost4 = calculate_bid((0,0), (1,1), 0.0)
    assert cost4 == float('inf')
    
    print("SUCCESS: Bid function verified.")
