from abc import ABC, abstractmethod
from typing import Callable, Any
import zenoh
import random
import threading

class TransportABC(ABC):
    @abstractmethod
    def publish(self, topic: str, payload: bytes):
        """Publishes a byte payload to a given topic."""
        pass
        
    @abstractmethod
    def subscribe(self, topic: str, callback: Callable[[str, bytes], None]) -> Any:
        """Subscribes to a topic and invokes callback(topic, payload) on messages."""
        pass
        
    @abstractmethod
    def close(self):
        """Closes the transport connection."""
        pass

class ZenohTransport(TransportABC):
    def __init__(self, mode: str = "peer"):
        conf = zenoh.Config()
        conf.insert_json5("mode", f'"{mode}"')
        self.session = zenoh.open(conf)
        self.publishers = {}
        self.subscribers = {}
        
    def publish(self, topic: str, payload: bytes):
        if topic not in self.publishers:
            self.publishers[topic] = self.session.declare_publisher(topic)
        self.publishers[topic].put(payload)
        
    def subscribe(self, topic: str, callback: Callable[[str, bytes], None]) -> Any:
        def _callback(sample):
            topic_str = str(sample.key_expr)
            callback(topic_str, sample.payload.to_bytes())
            
        sub = self.session.declare_subscriber(topic, _callback)
        self.subscribers[topic] = sub
        return sub
        
    def close(self):
        self.session.close()

import socket
import struct
import threading

class UdpMulticastTransport(TransportABC):
    def __init__(self, mcast_grp: str = '224.1.1.1', port: int = 5007):
        self.mcast_grp = mcast_grp
        self.port = port
        self.running = True
        
        # Publisher socket
        self.pub_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.pub_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        
        # Subscriber socket
        self.sub_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            self.sub_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except AttributeError:
            pass
            
        self.sub_sock.bind(('', self.port))
        
        mreq = struct.pack("4sl", socket.inet_aton(self.mcast_grp), socket.INADDR_ANY)
        self.sub_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        self.callbacks = {}
        
        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.recv_thread.start()
        
    def _recv_loop(self):
        while self.running:
            try:
                self.sub_sock.settimeout(0.5)
                data, _ = self.sub_sock.recvfrom(65535)
                parts = data.split(b'|', 1)
                if len(parts) == 2:
                    topic = parts[0].decode('utf-8')
                    payload = parts[1]
                    for sub_topic, cb in self.callbacks.items():
                        if sub_topic == topic: # Direct match for UDP fallback
                            cb(topic, payload)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"UDP Recv Error: {e}")

    def publish(self, topic: str, payload: bytes):
        msg = topic.encode('utf-8') + b'|' + payload
        self.pub_sock.sendto(msg, (self.mcast_grp, self.port))

    def subscribe(self, topic: str, callback: Callable[[str, bytes], None]) -> Any:
        self.callbacks[topic] = callback
        return topic

    def close(self):
        self.running = False
        try:
            self.pub_sock.close()
            self.sub_sock.close()
        except Exception:
            pass

class InProcessTransport(TransportABC):
    def __init__(self):
        # Maps topic -> list of callbacks
        self.callbacks = {}

    def publish(self, topic: str, payload: bytes):
        if topic in self.callbacks:
            for cb in self.callbacks[topic]:
                cb(topic, payload)

    def subscribe(self, topic: str, callback: Callable[[str, bytes], None]) -> Any:
        if topic not in self.callbacks:
            self.callbacks[topic] = []
        self.callbacks[topic].append(callback)
        return callback

    def close(self):
        self.callbacks.clear()

class LossyTransport(TransportABC):
    def __init__(self, inner: TransportABC, drop_prob: float = 0.1, min_delay: float = 0.010, max_delay: float = 0.050):
        self.inner = inner
        self.drop_prob = drop_prob
        self.min_delay = min_delay
        self.max_delay = max_delay

    def publish(self, topic: str, payload: bytes):
        if random.random() < self.drop_prob:
            return # Dropped
            
        delay = random.uniform(self.min_delay, self.max_delay)
        threading.Timer(delay, self.inner.publish, args=[topic, payload]).start()

    def subscribe(self, topic: str, callback: Callable[[str, bytes], None]) -> Any:
        return self.inner.subscribe(topic, callback)

    def close(self):
        self.inner.close()

if __name__ == "__main__":
    import time
    import sys
    import argparse
    import random

    parser = argparse.ArgumentParser(description="Test Transports")
    parser.add_argument("--pub", action="store_true", help="Run as publisher")
    parser.add_argument("--sub", action="store_true", help="Run as subscriber")
    parser.add_argument("--udp", action="store_true", help="Use UDP fallback instead of Zenoh")
    parser.add_argument("--inmem", action="store_true", help="Use In-process memory transport")
    parser.add_argument("--lossy", action="store_true", help="Wrap transport in LossyTransport for testing drop rate")
    args = parser.parse_args()

    if args.udp:
        base_transport = UdpMulticastTransport()
    elif args.inmem:
        base_transport = InProcessTransport()
    else:
        base_transport = ZenohTransport(mode="peer")
        
    transport = LossyTransport(base_transport) if args.lossy else base_transport

    topic = "vyuha/test/p2p"

    if args.lossy and not args.pub and not args.sub:
        print("Testing LossyTransport Drop Rate...")
        received = []
        def on_msg(t: str, payload: bytes):
            received.append(payload)
            
        transport.subscribe(topic, on_msg)
        
        num_msgs = 100
        for i in range(num_msgs):
            transport.publish(topic, b"data")
            
        time.sleep(1.0) # wait for all delayed messages
        
        drop_rate = 1.0 - (len(received) / float(num_msgs))
        print(f"Sent {num_msgs}, Received {len(received)}, Drop Rate: {drop_rate:.2f}")
        assert 0.0 < drop_rate < 0.3, "Drop rate should be roughly around 10%"
        print("SUCCESS: LossyTransport verified.")
        transport.close()
        sys.exit(0)

    if args.sub:
        print("Starting Subscriber Node...")
        def on_msg(t: str, payload: bytes):
            print(f"[SUB] Received on '{t}': {payload.decode('utf-8')}")
        transport.subscribe(topic, on_msg)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    elif args.pub:
        print("Starting Publisher Node...")
        time.sleep(1) # Wait for discovery
        for i in range(5):
            msg = f"Message {i} from publisher"
            print(f"[PUB] Broadcasting: {msg}")
            transport.publish(topic, msg.encode('utf-8'))
            time.sleep(1)
            
    else:
        # Default behavior: run both in same process
        print("Testing Transport in same process...")
        received = []
        def on_msg(t: str, payload: bytes):
            received.append(payload)
            
        transport.subscribe(topic, on_msg)
        time.sleep(1)
        transport.publish(topic, b"Self-ping")
        time.sleep(1)
        assert len(received) == 1
        print("SUCCESS: In-process test passed. Use --pub and --sub for multi-process test.")

    transport.close()
