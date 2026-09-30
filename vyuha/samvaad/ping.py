import zenoh
import time
import os
import sys

robot_id = os.environ.get("ROBOT_ID", "UNKNOWN")

if __name__ == "__main__":
    print(f"[{robot_id}] Starting Zenoh ping node...")
    
    # Simple configuration, Zenoh handles discovery automatically (e.g. over multicast)
    conf = zenoh.Config()
    session = zenoh.open(conf)
    
    topic = f"vyuha/robot/{robot_id}/ping"
    pub = session.declare_publisher(topic)
    
    for i in range(5):
        msg = f"Ping {i} from {robot_id}"
        pub.put(msg)
        print(f"[{robot_id}] Broadcasted: {msg}")
        time.sleep(1)
        
    session.close()
    print(f"[{robot_id}] Zenoh ping complete.")
