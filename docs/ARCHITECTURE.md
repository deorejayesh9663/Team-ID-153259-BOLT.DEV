# VYUHA Architecture Specification
**Status:** FINAL SIGN-OFF (v1.0)
**Project Code:** SIH26123 - Bharat Electronics Limited

## 1. System Overview
**VYUHA** is an edge-native, decentralized coordination framework designed for multi-agent autonomous mobile robots (AMRs) operating in dynamic smart warehouses. It eliminates the single point of failure (SPOF) inherent in traditional cloud-based fleet managers.

## 2. The Four Pillars

### 2.1 VYUHA-Core (Edge Autonomy)
- **Deployment:** Runs directly on edge compute (Raspberry Pi 5 or Jetson Orin Nano) onboard each robot.
- **Execution Budget:** Proven to resolve complex PIBT multi-agent conflicts in < 0.1 ms for a 50-robot cluster, consuming < 1% of the Pi 5's CPU budget, leaving the rest for LiDAR SLAM and Nav2.
- **Safety Invariant:** A strict, mathematical right-of-way arbiter guarantees zero collisions. AI models provide advisory cost-maps only and cannot override the deterministic safety layer.

### 2.2 SAMVAAD (Decentralized Mesh)
- **Protocol:** Zenoh peer-to-peer (P2P) mode over ROS 2 `rmw_zenoh_cpp`.
- **Discovery:** UDP Multicast with zero central brokers.
- **Resilience:** Gracefully degrades to LiDAR-only safe mode during Wi-Fi blackouts and re-syncs state via CRDT gossip when connectivity returns.

### 2.3 NETRA (Digital Twin Dashboard)
- **Architecture:** React + Vite client interacting via a Python WebSocket sink.
- **Role:** Purely observational. NETRA provides pixel-art visualizations, live telemetry (TRACES, MESH, BUILD), and an operator control rail for chaos injections.
- **SPOF Proof:** Killing the NETRA dashboard has zero impact on fleet coordination. 

### 2.4 KASOTI (Benchmark Harness)
- **Validation:** Provides automated, deterministic benchmark suites pitting VYUHA against traditional stop-and-wait systems.
- **Results:** Consistently achieves a ~37% reduction in makespan in 400-run randomized Monte Carlo matrices with a hard guarantee of zero collisions.

## 3. Data Flow & Latency Budget
1. **Perception (LiDAR/Odom):** Processed locally.
2. **Mesh Sync (SAMVAAD):** < 15ms latency over Wi-Fi 6.
3. **Conflict Arbitration (VYUHA-Core):** < 0.1ms per tick.
4. **Hardware Execution (ROS2 Bridge):** Translated from abstract grid coordinate to micro-ROS `Twist` command in < 0.05ms.

## 4. Final Sign-Off
All architectural requirements defined in the Traceability Matrix (`docs/TRACEABILITY.md`) have been verified against physical or simulated tests. The architecture is approved for SIH 2026 Finals presentation.
