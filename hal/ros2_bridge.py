import json
import math
import logging
from typing import Dict, Tuple

# Mocking rclpy for local development without ROS 2 installed.
# In a real deployment, these would be:
# import rclpy
# from rclpy.node import Node
# from geometry_msgs.msg import Twist
# from nav_msgs.msg import Odometry
# from sensor_msgs.msg import BatteryState
try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist
    from nav_msgs.msg import Odometry
    from sensor_msgs.msg import BatteryState
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False
    
    # Mock classes for offline development
    class Node:
        def __init__(self, name):
            self.name = name
            
        def create_publisher(self, msg_type, topic, qos):
            return MockPublisher(topic)
            
        def create_subscription(self, msg_type, topic, callback, qos):
            return MockSubscription(topic)
            
        def get_logger(self):
            return logging.getLogger(self.name)

    class Twist:
        def __init__(self):
            self.linear = type('vec3', (), {'x': 0.0, 'y': 0.0, 'z': 0.0})()
            self.angular = type('vec3', (), {'x': 0.0, 'y': 0.0, 'z': 0.0})()

    class Odometry:
        pass

    class BatteryState:
        pass

    class MockPublisher:
        def __init__(self, topic):
            self.topic = topic
            
        def publish(self, msg):
            # In simulation, we just log the twist command
            pass

    class MockSubscription:
        def __init__(self, topic):
            self.topic = topic


class VyuhaRosBridge(Node):
    """
    ROS 2 Bridge Node for VYUHA.
    Translates discrete grid-based commands from VYUHA-Core into continuous
    velocity commands (Twist) for physical hardware.
    """
    
    def __init__(self, robot_ids: list, grid_resolution: float = 1.0):
        """
        :param robot_ids: List of robot string IDs to manage (e.g., ['r1', 'r2'])
        :param grid_resolution: Physical size of one grid cell in meters
        """
        super().__init__('vyuha_ros_bridge')
        self.grid_resolution = grid_resolution
        
        self.publishers_cmd_vel = {}
        self.subscribers_odom = {}
        self.subscribers_battery = {}
        
        # Real-world state tracked from Odometry
        self.robot_states = {
            r_id: {"x": 0.0, "y": 0.0, "theta": 0.0, "battery": 100.0} 
            for r_id in robot_ids
        }
        
        for r_id in robot_ids:
            # Publishers
            pub = self.create_publisher(Twist, f'/{r_id}/cmd_vel', 10)
            self.publishers_cmd_vel[r_id] = pub
            
            # Subscribers
            # We use lambdas with default arguments to capture the current r_id in the loop
            sub_odom = self.create_subscription(
                Odometry, 
                f'/{r_id}/odom', 
                lambda msg, rid=r_id: self._odom_callback(rid, msg), 
                10
            )
            self.subscribers_odom[r_id] = sub_odom
            
            sub_batt = self.create_subscription(
                BatteryState, 
                f'/{r_id}/battery', 
                lambda msg, rid=r_id: self._battery_callback(rid, msg), 
                10
            )
            self.subscribers_battery[r_id] = sub_batt
            
        self.get_logger().info(f"VyuhaRosBridge initialized for {len(robot_ids)} robots.")
        
    def _odom_callback(self, r_id: str, msg: Odometry):
        """Handle incoming odometry updates from hardware."""
        if not ROS2_AVAILABLE:
            return
            
        # Extract pose (assuming standard nav_msgs/Odometry)
        pos = msg.pose.pose.position
        # Simplified quaternion to yaw conversion for 2D movement
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        
        self.robot_states[r_id]["x"] = pos.x
        self.robot_states[r_id]["y"] = pos.y
        self.robot_states[r_id]["theta"] = yaw

    def _battery_callback(self, r_id: str, msg: BatteryState):
        """Handle incoming battery telemetry."""
        if not ROS2_AVAILABLE:
            return
        self.robot_states[r_id]["battery"] = msg.percentage * 100.0
        
    def get_discrete_position(self, r_id: str) -> Tuple[int, int]:
        """Convert continuous real-world coordinates back to discrete grid cells."""
        state = self.robot_states[r_id]
        grid_x = int(round(state["x"] / self.grid_resolution))
        grid_y = int(round(state["y"] / self.grid_resolution))
        return (grid_x, grid_y)
        
    def send_move_command(self, r_id: str, target_grid_x: int, target_grid_y: int):
        """
        Called by VYUHA-Core to move a robot to an adjacent grid cell.
        Translates the grid request into a continuous Twist message.
        """
        if r_id not in self.publishers_cmd_vel:
            self.get_logger().error(f"Unknown robot {r_id}")
            return
            
        # Convert target grid to real-world continuous target
        target_real_x = target_grid_x * self.grid_resolution
        target_real_y = target_grid_y * self.grid_resolution
        
        state = self.robot_states[r_id]
        current_x = state["x"]
        current_y = state["y"]
        current_theta = state["theta"]
        
        # Calculate heading and distance
        dx = target_real_x - current_x
        dy = target_real_y - current_y
        distance = math.hypot(dx, dy)
        target_heading = math.atan2(dy, dx)
        
        # Simple proportional controller for differential drive
        twist = Twist()
        
        # Heading error (normalized between -pi and pi)
        heading_error = target_heading - current_theta
        heading_error = (heading_error + math.pi) % (2 * math.pi) - math.pi
        
        # If we are far off our heading, rotate in place first
        if abs(heading_error) > 0.1: # approx 5.7 degrees
            twist.angular.z = max(-1.0, min(1.0, heading_error * 2.0)) # P-control for rotation
            twist.linear.x = 0.0
        else:
            # Move forward towards target
            twist.angular.z = heading_error * 0.5 # keep correcting heading
            twist.linear.x = max(-0.5, min(0.5, distance * 1.0)) # P-control for translation
            
        self.publishers_cmd_vel[r_id].publish(twist)

def main():
    if ROS2_AVAILABLE:
        rclpy.init()
        
    bridge = VyuhaRosBridge(robot_ids=['r1', 'r2', 'r3'], grid_resolution=1.0)
    
    if ROS2_AVAILABLE:
        try:
            rclpy.spin(bridge)
        except KeyboardInterrupt:
            pass
        finally:
            bridge.destroy_node()
            rclpy.shutdown()
    else:
        print("ROS 2 not installed. Running in mock mode.")
        # Simulate a command
        bridge.send_move_command('r1', 1, 0)
        print("Mock command sent successfully.")

if __name__ == '__main__':
    main()
