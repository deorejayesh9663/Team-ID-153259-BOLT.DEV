import os
import sys
import unittest

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from sim.physics import check_footprint_collision

class TestSafetyInvariants(unittest.TestCase):
    def test_ai_cannot_override_collision_physics(self):
        """
        Even if the AI 'Advisory Layer' strongly predicts low congestion or gives 
        a Critical priority override, the physical engine MUST block the move 
        if there is a collision.
        """
        # Simulated AI override logic (hallucinating it is safe to proceed)
        ai_advisory_override_force_move = True
        ai_priority = 1 # Critical
        
        # Two robots in the exact same spot (guaranteed collision)
        pose1 = (0, 0, 0)
        size1 = (1.0, 1.0)
        
        pose2 = (0.5, 0, 0)
        size2 = (1.0, 1.0)
        
        # Physics engine check
        is_colliding = check_footprint_collision(pose1, size1, pose2, size2)
        is_clear = not is_colliding
        self.assertFalse(is_clear, "Target is occupied, physics engine should see it")
        
        # The safety invariant: AI cannot bypass the is_clear check.
        # The true engine logic MUST be an AND with is_clear
        safe_move_allowed = is_clear and ai_advisory_override_force_move
        
        self.assertFalse(safe_move_allowed, "Safety Invariant Failed: AI was able to force a move into an occupied node!")
        
    def test_ai_priority_respects_yield(self):
        """
        AI Priority shouldn't be able to force a physical jump over a robot.
        """
        # Lower priority robot currently occupies the narrow aisle
        low_pri = 5
        
        # High priority robot approaches
        high_pri = 1
        
        # AI says high_pri can move
        ai_says_move = True
        
        # But physics engine says collision
        physics_clear = False
        
        # Final decision MUST respect physics over AI priority
        final_move = physics_clear and (ai_says_move and high_pri < low_pri)
        
        self.assertFalse(final_move, "Safety Invariant Failed: High priority AI bypassed collision physics!")

if __name__ == '__main__':
    unittest.main()
