import numpy as np
from scipy.optimize import linear_sum_assignment

def assign_tasks_hungarian(robots: dict, tasks: dict) -> dict:
    """
    Globally optimal task assignment using the Hungarian Algorithm (O(N^3)).
    robots: { robot_id: (x, y) }
    tasks: { task_id: (x, y) }
    
    Returns: { task_id: robot_id }
    """
    robot_ids = list(robots.keys())
    task_ids = list(tasks.keys())
    
    if not robot_ids or not task_ids:
        return {}
        
    # Cost matrix (Manhattan distance)
    cost_matrix = np.zeros((len(robot_ids), len(task_ids)))
    
    for i, r_id in enumerate(robot_ids):
        rx, ry = robots[r_id]
        for j, t_id in enumerate(task_ids):
            tx, ty = tasks[t_id]
            cost_matrix[i, j] = abs(rx - tx) + abs(ry - ty)
            
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    
    assignments = {}
    for r_idx, t_idx in zip(row_ind, col_ind):
        assignments[task_ids[t_idx]] = robot_ids[r_idx]
        
    return assignments

if __name__ == "__main__":
    print("Testing Hungarian Algorithm Assignment (Baseline SPOF)...")
    
    robots = {
        "AMR_1": (0, 0),
        "AMR_2": (10, 10),
        "AMR_3": (5, 5)
    }
    
    tasks = {
        "T_001": (1, 1),
        "T_002": (9, 9),
        "T_003": (6, 4)
    }
    
    assignments = assign_tasks_hungarian(robots, tasks)
    
    print("Global optimal assignments:")
    for t_id, r_id in assignments.items():
        print(f"Task {t_id} assigned to {r_id}")
        
    assert assignments["T_001"] == "AMR_1"
    assert assignments["T_002"] == "AMR_2"
    assert assignments["T_003"] == "AMR_3"
    
    print("SUCCESS: Hungarian algorithm bulk assignment verified.")
