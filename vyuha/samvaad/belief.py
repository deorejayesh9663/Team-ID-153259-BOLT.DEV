import zenoh
import json
import time
import sys
import threading

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

class BeliefPublisher:
    def __init__(self, robot_id: str):
        self.robot_id = robot_id
        conf = zenoh.Config()
        self.session = zenoh.open(conf)
        self.topic = f"vyuha/robot/{self.robot_id}/state"
        self.publisher = self.session.declare_publisher(self.topic)

    def publish_state(self, x: float, y: float, theta: float, battery: float):
        state = {
            "robot_id": self.robot_id,
            "x": x,
            "y": y,
            "theta": theta,
            "battery": battery,
            "timestamp": time.time()
        }
        payload = json.dumps(state)
        self.publisher.put(payload)
        print(f"[PUB] {self.robot_id} broadcasted state: {payload}")

    def close(self):
        self.session.close()

class BeliefSubscriber:
    def __init__(self, topic: str = "vyuha/robot/*/state"):
        conf = zenoh.Config()
        self.session = zenoh.open(conf)
        self.subscriber = self.session.declare_subscriber(topic, self._on_message)
        self.received_messages = []

    def _on_message(self, sample):
        payload = sample.payload.to_bytes().decode('utf-8')
        print(f"[SUB] Received on '{sample.key_expr}': {payload}")
        self.received_messages.append(json.loads(payload))

    def close(self):
        self.session.close()

if __name__ == "__main__":
    print("Testing Zenoh Belief State Pub/Sub...")
    
    # 1. Start subscriber in background
    sub = BeliefSubscriber()
    time.sleep(1) # wait for zenoh discovery
    
    # 2. Start publisher
    pub = BeliefPublisher("AMR_1")
    time.sleep(1) # wait for session
    
    # 3. Publish a state
    pub.publish_state(10.5, 2.0, 1.57, 98.0)
    
    # Wait a bit for message to propagate over localhost multicast
    time.sleep(2)
    
    pub.close()
    sub.close()
    
    if len(sub.received_messages) > 0:
        print("SUCCESS: Another node received and printed JSON location.")
    else:
        print("FAILED: No messages received.")
        sys.exit(1)
