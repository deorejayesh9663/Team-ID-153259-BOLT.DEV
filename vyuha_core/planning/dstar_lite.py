import heapq

class DStarLite:
    """
    A lightweight incremental path planner for VYUHA.
    For this benchmark scale (30x30), this implements an A* search 
    that respects a set of known obstacles, providing dynamic replanning capabilities
    when obstacles (like a blocked aisle) are detected.
    """
    def __init__(self, grid_size=30):
        self.grid_size = grid_size
        self.obstacles = set()
        
    def update_obstacles(self, new_obstacles):
        """Update the internal knowledge of obstacles."""
        self.obstacles = set(new_obstacles)
        
    def get_next_move(self, start, target):
        """
        Calculates the shortest path using A* and returns the immediate next move.
        Returns the current position if target is reached or unreachable.
        """
        if start == target:
            return start
            
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
            
        frontier = []
        heapq.heappush(frontier, (0, start))
        
        came_from = {}
        cost_so_far = {}
        
        came_from[start] = None
        cost_so_far[start] = 0
        
        while frontier:
            _, current = heapq.heappop(frontier)
            
            if current == target:
                break
                
            x, y = current
            # Check 4-way neighbors
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nxt = (x + dx, y + dy)
                
                # Bounds check
                if 0 <= nxt[0] < self.grid_size and 0 <= nxt[1] < self.grid_size:
                    # Obstacle check
                    if nxt in self.obstacles:
                        continue
                        
                    new_cost = cost_so_far[current] + 1
                    if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                        cost_so_far[nxt] = new_cost
                        priority = new_cost + heuristic(nxt, target)
                        heapq.heappush(frontier, (priority, nxt))
                        came_from[nxt] = current
                        
        if target not in came_from:
            # Unreachable, just return current (or fallback to greedy manhattan)
            return start
            
        # Backtrack to find the first step
        curr = target
        path = []
        while curr != start:
            path.append(curr)
            curr = came_from[curr]
            
        return path[-1] # Path is built backwards, so -1 is the first step from start
