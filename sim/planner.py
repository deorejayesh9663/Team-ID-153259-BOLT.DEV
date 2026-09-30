import heapq
import os
import sys

# Add current dir to sys.path so we can import warehouse if run as a script
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from warehouse import WarehouseMap

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

class AStarPlanner:
    def __init__(self, warehouse_map: WarehouseMap):
        self.map = warehouse_map
        self.width = warehouse_map.width
        self.height = warehouse_map.height
        self.layout = warehouse_map.layout

    def is_traversable(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        # R is rack, not traversable. Everything else is traversable for basic planning.
        if self.layout[y][x] == 'R':
            return False
        return True

    def heuristic(self, a, b):
        # Manhattan distance
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def plan(self, start, goal):
        """Returns a list of (x,y) tuples from start to goal, or None if no path."""
        if not self.is_traversable(*start) or not self.is_traversable(*goal):
            return None

        # Priority queue for open set
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        came_from = {}
        
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path

            # 4-way movement
            neighbors = [
                (current[0]+1, current[1]),
                (current[0]-1, current[1]),
                (current[0], current[1]+1),
                (current[0], current[1]-1)
            ]

            for nxt in neighbors:
                if not self.is_traversable(*nxt):
                    continue
                
                tentative_g_score = g_score[current] + 1
                
                if nxt not in g_score or tentative_g_score < g_score[nxt]:
                    came_from[nxt] = current
                    g_score[nxt] = tentative_g_score
                    f_score[nxt] = tentative_g_score + self.heuristic(nxt, goal)
                    heapq.heappush(open_set, (f_score[nxt], nxt))

        return None

if __name__ == "__main__":
    map_path = os.path.join(current_dir, "maps", "small_3amr.json")
    warehouse = WarehouseMap(map_path)
    planner = AStarPlanner(warehouse)
    
    start_pos = (0, 0) # D at top left
    goal_pos = (19, 14) # P at bottom right
    
    print(f"Planning from {start_pos} to {goal_pos}...")
    path = planner.plan(start_pos, goal_pos)
    
    if path:
        print(f"SUCCESS: Path found! Length: {len(path)}")
        print(path)
        
        print("\nVisualized Path:")
        # Optionally print ascii map with path
        for y in range(warehouse.height):
            row_str = ""
            for x in range(warehouse.width):
                if (x, y) == start_pos:
                    row_str += "S"
                elif (x, y) == goal_pos:
                    row_str += "G"
                elif (x, y) in path:
                    row_str += "*"
                else:
                    char = warehouse.layout[y][x]
                    if char == '.': row_str += ' '
                    elif char == 'R': row_str += '▓'
                    elif char == 'J': row_str += '◆'
                    elif char == 'P': row_str += 'P'
                    elif char == 'D': row_str += 'D'
                    elif char == 'C': row_str += '⚡'
                    else: row_str += char
            print(row_str)
            
    else:
        print("No path found!")
        sys.exit(1)
