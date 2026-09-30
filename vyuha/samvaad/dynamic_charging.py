class DynamicChargeThreshold:
    """
    AI-Based Dynamic Battery Charging Threshold logic.
    Instead of a hardcoded 20% return-to-dock threshold, this module dynamically
    adjusts the threshold based on the predicted busyness of the warehouse shift.
    """
    def __init__(self, base_threshold=20.0):
        self.base_threshold = base_threshold
        self.current_threshold = base_threshold

    def update_threshold(self, shift_intensity, pending_tasks, fleet_size):
        """
        Adjusts the charging threshold.
        - If shift intensity is high (e.g., morning dispatch), robots should hold off charging
          until absolutely necessary to maximize throughput (lower threshold).
        - If shift intensity is low (e.g., night shift), robots should charge early and often
          so they are at 100% when the busy shift starts (higher threshold).
        """
        # Simple heuristic mapping
        # shift_intensity is a value from 0.0 (idle) to 1.0 (peak)
        
        # Max drop is 10%, max increase is 30%
        if shift_intensity > 0.8:
            # Very busy: risk running lower
            self.current_threshold = self.base_threshold - 5.0
        elif shift_intensity < 0.3:
            # Very quiet: charge aggressively
            self.current_threshold = self.base_threshold + 20.0
        else:
            self.current_threshold = self.base_threshold
            
        return self.current_threshold

    def should_charge(self, current_battery_soc):
        return current_battery_soc <= self.current_threshold
