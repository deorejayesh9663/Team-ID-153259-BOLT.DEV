# Requirement Traceability Matrix (RTM)
**Project:** VYUHA
**Status:** FINAL (Phase P10)

| # | Requirement | VYUHA Module | Evidence / Test | Status |
|---|---|---|---|---|
| R1 | Share current position | `SAMVAAD → POSE` broadcast @ 10 Hz | `test_pose_propagation.py` | ✅ PASS |
| R2 | Communicate intended path | `SAMVAAD → INTENT` (N-step lookahead) | `test_intent_horizon.py` | ✅ PASS |
| R3 | Exchange localization info | `SAMVAAD → LOCALIZE` (pose + covariance) | `test_covariance_merge.py` | ✅ PASS |
| R4 | No central server dependency | Zenoh **peer mode**, zero brokers | `test_kill_all_servers.py` | ✅ PASS |
| R5 | Resolve deadlocks | Wait-for-graph cycle detection + priority recovery | `test_deadlock_4way.py` | ✅ PASS |
| R6 | Prevent collisions | Space-time reservation table (vertex + edge) | `test_zero_collisions.py` | ✅ PASS |
| R7 | Narrow intersections | Junction token / mutex cell lock | `test_single_width_aisle.py` | ✅ PASS |
| R8 | Choke point handling | Congestion-cost inflation on A* | `test_chokepoint_flow.py` | ✅ PASS |
| R9 | Overlapping paths | PIBT priority inheritance + backtracking | `test_head_on_swap.py` | ✅ PASS |
| R10 | Blocked aisle → re-route | `BLOCKED` gossip + D* Lite incremental replan | `test_dynamic_obstacle.py` | ✅ PASS |
| R11 | Re-assign pickup points | Contract Net re-auction on task release | `test_task_reassignment.py` | ✅ PASS |
| R12 | Fleet re-coordination | Global intent invalidation + cascade replan | `test_cascade_replan.py` | ✅ PASS |
| R13 | Runs on edge hardware | CPU/RAM profile on Pi 5 class budget | `bench_edge_profile.py` | ✅ PASS |
| R14 | Dashboard — positions | NETRA live warehouse twin | Visual + screenshot evidence | ✅ PASS |
| R15 | Dashboard — fleet activity | NETRA fleet strip + event log | Visual + screenshot evidence | ✅ PASS |
| R16 | Dashboard — battery | NETRA battery ring per AMR | Visual + screenshot evidence | ✅ PASS |
| R17 | ≥3 AMRs | Configurable `fleet_size` (tested 3 / 4 / 6 / 8 / 12) | `bench_scaling.py` | ✅ PASS |
| R18 | Dynamic environment | Runtime obstacle injection, human actors | `test_chaos_suite.py` | ✅ PASS |
| R19 | (P7) Intent bubble layer | NETRA visualizes intent over AMR | UI Test | ✅ PASS |
| R20 | (P7) Read-only telemetry | NETRA has no control over core fleet logic | Code inspection (`ControlRail.jsx`) | ✅ PASS |
| R21 | (P8) Blackout Chaos | C5 injects total server/network loss | Chaos Suite | ✅ PASS |
| R22 | (P8) AI Toggle | Live A/B AI-advisor OFF toggle | UI Test | ✅ PASS |
| R23 | (P9) ROS 2 Bridge | Translates Discrete Grid to Twist/Odom | `hal/ros2_bridge.py` | ✅ PASS |
| R24 | (P9) ESP32 Stub | Mocks real-world latency over micro-ROS | `hal/esp32_stub.ino` | ✅ PASS |
| R25 | (P9) E2E Hardware Test | Verifies <5ms latency from core to motor | `scripts/e2e_hardware_test.py` | ✅ PASS |
| R26 | (P10) 400-run matrix | Automated throughput/latency sweeps | `scripts/run_benchmarks.py` | ✅ PASS |
| R27 | (P10) Metric graphs | Visualizes fleet scalability | `scripts/generate_graphs.py` | ✅ PASS |
| **S1** | **Zero collisions** | Deterministic arbiter + physical occupancy assert | `KASOTI` benchmark report | ✅ PASS |
| **S2** | **≥20% faster than stop-and-wait** | Baseline vs. VYUHA A/B harness | `KASOTI` benchmark report | ✅ PASS |

**Final Audit Sign-Off:** Complete and verified. All 30 requirements and success gates successfully satisfied.
