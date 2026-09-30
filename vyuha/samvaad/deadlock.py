class WaitForGraph:
    def __init__(self):
        # adjacency list: waiting_robot -> set(blocking_robots)
        self.adj = {}

    def add_intent(self, waiting_robot: str, blocking_robot: str):
        """Records that waiting_robot wants a resource currently held by blocking_robot."""
        if waiting_robot not in self.adj:
            self.adj[waiting_robot] = set()
        if blocking_robot not in self.adj:
            self.adj[blocking_robot] = set()
            
        self.adj[waiting_robot].add(blocking_robot)

    def has_cycle(self) -> bool:
        """Simple DFS to detect if any cycle exists in the wait-for graph."""
        visited = set()
        rec_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.adj.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
                    
            rec_stack.remove(node)
            return False

        for node in self.adj:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def find_sccs(self) -> list[list[str]]:
        """Tarjan's strongly connected components algorithm."""
        index_counter = [0]
        index = {}
        lowlink = {}
        stack = []
        on_stack = set()
        sccs = []
        
        nodes = set(self.adj.keys())
        for v in self.adj.values():
            nodes.update(v)

        def strongconnect(node):
            index[node] = index_counter[0]
            lowlink[node] = index_counter[0]
            index_counter[0] += 1
            stack.append(node)
            on_stack.add(node)

            for neighbor in self.adj.get(node, []):
                if neighbor not in index:
                    strongconnect(neighbor)
                    lowlink[node] = min(lowlink[node], lowlink[neighbor])
                elif neighbor in on_stack:
                    lowlink[node] = min(lowlink[node], index[neighbor])

            if lowlink[node] == index[node]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.append(w)
                    if w == node:
                        break
                sccs.append(scc)

        for node in nodes:
            if node not in index:
                strongconnect(node)
                
        return sccs

if __name__ == "__main__":
    print("Testing WaitForGraph builder...")
    
    wfg = WaitForGraph()
    # A wants B's spot, B wants A's spot
    wfg.add_intent("AMR_A", "AMR_B")
    wfg.add_intent("AMR_B", "AMR_A")
    
    assert wfg.has_cycle() == True, "Cycle should be detected for A->B, B->A"
    
    sccs = wfg.find_sccs()
    cycles = [s for s in sccs if len(s) > 1]
    assert len(cycles) == 1, "Should find 1 cycle"
    assert set(cycles[0]) == {"AMR_A", "AMR_B"}
    print("Cycle correctly detected via Tarjan's (A->B, B->A)")
    
    wfg2 = WaitForGraph()
    wfg2.add_intent("AMR_A", "AMR_B")
    wfg2.add_intent("AMR_B", "AMR_C")
    wfg2.add_intent("AMR_C", "AMR_A")
    
    sccs2 = wfg2.find_sccs()
    cycles2 = [s for s in sccs2 if len(s) > 1]
    assert len(cycles2) == 1, "Should find 1 cycle"
    assert set(cycles2[0]) == {"AMR_A", "AMR_B", "AMR_C"}
    print("Cycle correctly identified (A->B->C->A)")
    
    print("SUCCESS: Tarjan SCC builder verified.")
    print("-" * 40)

class PIBTRunner:
    """Priority Inheritance with Backtracking (PIBT) for multi-agent pathfinding."""
    def __init__(self, agents: dict, get_valid_moves: callable):
        # agents format: { agent_id: {'pos': (x,y), 'target': (x,y), 'priority': int} }
        self.agents = agents
        self.get_valid_moves = get_valid_moves
        self.next_positions = {}
        
    def run(self) -> dict:
        self.next_positions = {}
        # Sort agents by priority (highest first)
        sorted_agents = sorted(self.agents.keys(), key=lambda a: self.agents[a]['priority'], reverse=True)
        
        for agent_id in sorted_agents:
            if agent_id not in self.next_positions:
                self._pibt(agent_id)
                
        return self.next_positions
        
    def _pibt(self, agent_id: str, active: set = None) -> bool:
        if active is None:
            active = set()
            
        if agent_id in self.next_positions:
            return True
            
        if agent_id in active:
            # Resolution cycle detected, cannot proceed in this direction
            return False
            
        active.add(agent_id)
            
        pos = self.agents[agent_id]['pos']
        target = self.agents[agent_id]['target']
        
        moves = self.get_valid_moves(pos)
        moves = [m for m in moves if m != pos]
        # Sort moves by Manhattan distance to target
        moves.sort(key=lambda m: abs(m[0] - target[0]) + abs(m[1] - target[1]))
        
        # Include current position as a valid move (wait action) AT THE VERY END
        moves.append(pos)
        
        for v in moves:
            # Check if v is already claimed by a higher-priority / assigned agent
            if v in self.next_positions.values():
                continue
                
            # Check if v is currently physically occupied by another unassigned agent
            occupied_by = None
            for j_id, j_data in self.agents.items():
                if j_data['pos'] == v and j_id != agent_id:
                    occupied_by = j_id
                    break
                    
            if occupied_by:
                if occupied_by not in self.next_positions:
                    # Inherit priority and force j to move out of the way
                    success = self._pibt(occupied_by, active.copy())
                    if not success:
                        continue # Failed to move blocking agent, try next move
                
                # If j successfully moved out of v, we can claim v
                if self.next_positions.get(occupied_by) != v:
                    self.next_positions[agent_id] = v
                    return True
            else:
                # Free space
                self.next_positions[agent_id] = v
                return True
                
        # If all else fails, agent must wait at current pos
        self.next_positions[agent_id] = pos
        return False

if __name__ == "__main__":
    # PIBT test
    print("Testing PIBT Runner...")
    
    # 3x3 grid, AMR_1 at (1,1) wants (2,1)
    # AMR_2 at (2,1) wants (1,1). AMR_1 has higher priority.
    # AMR_2 should be forced out of the way to (2,0) or (2,2)
    agents = {
        "AMR_1": {"pos": (1,1), "target": (2,1), "priority": 10},
        "AMR_2": {"pos": (2,1), "target": (1,1), "priority": 5}
    }
    
    def get_valid_moves(pos):
        x, y = pos
        return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        
    pibt = PIBTRunner(agents, get_valid_moves)
    result = pibt.run()
    
    assert result["AMR_1"] == (2,1), f"AMR_1 should move to target. Got {result['AMR_1']}"
    assert result["AMR_2"] in [(2,0), (2,2), (3,1)], f"AMR_2 should yield. Got {result['AMR_2']}"
    
    print("SUCCESS: PIBT runner successfully resolved conflict by inheritance.")
