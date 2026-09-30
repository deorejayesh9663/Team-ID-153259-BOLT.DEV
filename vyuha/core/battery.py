class BatteryManager:
    def __init__(self, charge: float = 100.0, capacity: float = 100.0, 
                 discharge_rate_moving: float = 1.0, discharge_rate_idle: float = 0.1):
        self.charge = charge
        self.capacity = capacity
        self.discharge_rate_moving = discharge_rate_moving
        self.discharge_rate_idle = discharge_rate_idle
        self.is_charging = False
        
    def tick(self, dt: float, is_moving: bool):
        """Updates battery level based on time delta and movement state."""
        if self.is_charging:
            # Charges at 5% per second
            self.charge = min(self.capacity, self.charge + (5.0 * dt))
            return
            
        rate = self.discharge_rate_moving if is_moving else self.discharge_rate_idle
        self.charge = max(0.0, self.charge - (rate * dt))
        
    def needs_charging(self) -> bool:
        """Returns True if battery has dropped below the 20% reserve threshold."""
        return self.charge < 20.0
        
    def get_nearest_dock(self, current_pos: tuple, docks: list) -> tuple:
        """Finds the nearest charging dock using Manhattan distance."""
        if not docks:
            return None
        return min(docks, key=lambda d: abs(current_pos[0] - d[0]) + abs(current_pos[1] - d[1]))

if __name__ == "__main__":
    print("Testing BatteryManager...")
    
    bm = BatteryManager(charge=21.0)
    
    # Idle for 10 seconds
    bm.tick(10.0, is_moving=False)
    # 21.0 - (0.1 * 10) = 20.0
    assert bm.charge == 20.0
    assert not bm.needs_charging()
    
    # Move for 1 second
    bm.tick(1.0, is_moving=True)
    # 20.0 - 1.0 = 19.0
    assert bm.charge == 19.0
    assert bm.needs_charging()
    
    # Find nearest dock
    docks = [(10, 10), (0, 0), (5, 5)]
    nearest = bm.get_nearest_dock((1, 1), docks)
    assert nearest == (0, 0)
    
    # Charge
    bm.is_charging = True
    bm.tick(1.0, is_moving=False)
    assert bm.charge == 24.0
    
    print("SUCCESS: Battery manager verified.")
