class SpaceTimeTable:
    def __init__(self):
        # Maps (x, y, time_tick) -> robot_id
        self.reservations = {}

    def reserve(self, robot_id: str, x: int, y: int, time_tick: int) -> bool:
        """
        Attempts to reserve a spatial cell at a specific time tick.
        Returns True if successful (or already reserved by this robot), False if conflicting.
        """
        key = (x, y, time_tick)
        if key in self.reservations:
            if self.reservations[key] != robot_id:
                return False
            return True
            
        self.reservations[key] = robot_id
        return True

    def release(self, robot_id: str):
        """Releases all reservations for a specific robot."""
        keys_to_remove = [k for k, v in self.reservations.items() if v == robot_id]
        for k in keys_to_remove:
            del self.reservations[k]

class Arbiter:
    def __init__(self, table: SpaceTimeTable):
        self.table = table
        
    def request_reservation(self, robot_id: str, x: int, y: int, requested_time: int) -> int:
        """
        Attempts to reserve (x, y) at requested_time. 
        If blocked, yields (waits) by incrementing time until successful.
        Returns the actual time tick of the successful reservation.
        """
        current_time = requested_time
        while True:
            success = self.table.reserve(robot_id, x, y, current_time)
            if success:
                if current_time > requested_time:
                    print(f"[{robot_id}] Conflict resolved via arbiter. Yielded from t={requested_time} to t={current_time}")
                return current_time
            current_time += 1

if __name__ == "__main__":
    print("Testing SpaceTimeTable and Arbiter...")
    
    table = SpaceTimeTable()
    arbiter = Arbiter(table)
    
    # Robot 1 reserves cell A (10, 10) at t=5
    res1 = table.reserve("AMR_1", 10, 10, 5)
    print(f"AMR_1 reserving (10, 10) at t=5: {res1}")
    
    # Robot 2 attempts to reserve cell A (10, 10) at t=5 using arbiter
    print(f"AMR_2 requesting (10, 10) starting at t=5...")
    actual_t = arbiter.request_reservation("AMR_2", 10, 10, 5)
    
    assert actual_t == 6, f"AMR_2 should have yielded to t=6, but got t={actual_t}"
    
    print("SUCCESS: Deterministic conflict arbiter verified.")
