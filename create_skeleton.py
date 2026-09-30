import os

directories = [
    "vyuha_core/belief",
    "vyuha_core/planning",
    "vyuha_core/arbitration",
    "vyuha_core/edge_ai/models",
    "vyuha_core/tasks",
    "vyuha_core/power",
    "samvaad/transport",
    "netra/web",
    "netra/server",
    "netra/assets/sprites",
    "netra/assets/tiles",
    "sim/maps",
    "baseline",
    "kasoti/results",
    "ros2_ws/src/vyuha_ros/launch",
    "tests/unit",
    "tests/integration",
    "tests/safety",
    "tests/chaos",
    "docs"
]

files = [
    "vyuha_core/belief/world_model.py",
    "vyuha_core/belief/peer_registry.py",
    "vyuha_core/belief/blocked_cells.py",
    "vyuha_core/planning/astar.py",
    "vyuha_core/planning/dstar_lite.py",
    "vyuha_core/planning/reservation_table.py",
    "vyuha_core/planning/pibt.py",
    "vyuha_core/planning/orca.py",
    "vyuha_core/arbitration/conflict_arbiter.py",
    "vyuha_core/arbitration/deadlock_detector.py",
    "vyuha_core/arbitration/recovery.py",
    "vyuha_core/edge_ai/congestion_gru.py",
    "vyuha_core/edge_ai/priority_advisor.py",
    "vyuha_core/edge_ai/explain.py",
    "vyuha_core/tasks/contract_net.py",
    "vyuha_core/tasks/bid_function.py",
    "vyuha_core/tasks/task_model.py",
    "vyuha_core/power/battery_manager.py",
    "vyuha_core/runtime.py",
    "samvaad/transport/zenoh_peer.py",
    "samvaad/transport/udp_multicast.py",
    "samvaad/messages.py",
    "samvaad/gossip.py",
    "samvaad/crdt_merge.py",
    "samvaad/radio_model.py",
    "samvaad/security.py",
    "netra/web/warehouse_canvas.jsx",
    "netra/web/intent_bubbles.jsx",
    "netra/web/robot_panel.jsx",
    "netra/web/junction_inspector.jsx",
    "netra/web/fleet_strip.jsx",
    "netra/web/control_rail.jsx",
    "netra/server/telemetry_sink.py",
    "netra/server/trace_store.py",
    "netra/server/ws_gateway.py",
    "sim/warehouse.py",
    "sim/physics.py",
    "sim/actors.py",
    "sim/clock.py",
    "sim/maps/small_3amr.json",
    "sim/maps/medium_6amr.json",
    "sim/maps/large_12amr.json",
    "baseline/central_server.py",
    "baseline/stop_and_wait.py",
    "baseline/hungarian_assign.py",
    "kasoti/benchmark.py",
    "kasoti/metrics.py",
    "kasoti/report.py",
    "kasoti/chaos.py",
    "ros2_ws/src/vyuha_ros/vyuha_bridge_node.py",
    "ros2_ws/src/vyuha_ros/nav2_params.yaml",
    "docs/PROJECT.md",
    "docs/TECH_STACK.md",
    "docs/ARCHITECTURE.md",
    "docs/PROTOCOL.md",
    "docs/TRACEABILITY.md",
    "docs/BENCHMARK.md",
    "fleet_config.json",
    "requirements.txt",
    "docker-compose.yml",
    "README.md"
]

progress_content = """# VYUHA — Build Progress

Generated from BUILD_LOOP_PROMPT.md §3. Do not hand-edit checkmarks — let the loop agent update this file; edit only to add backlog notes.

## Phase P0 — Foundation (0/7)
- [ ] T-P0-01 — Scaffold the full repo tree
- [ ] T-P0-02 — requirements.txt + package.json installed clean
- [ ] T-P0-03 — Warehouse grid model
- [ ] T-P0-04 — Kinematics + footprint collision
- [ ] T-P0-05 — Deterministic seeded tick scheduler
- [ ] T-P0-06 — A* planner
- [ ] T-P0-07 — One robot completes one task solo

## Phase P1 — Multi-Agent Core (0/5)
- [ ] T-P1-01 — Belief State
- [ ] T-P1-02 — Space-time reservation table
- [ ] T-P1-03 — Deterministic conflict arbiter
- [ ] T-P1-04 — 3-robot scenario, zero collisions
- [ ] T-P1-05 — Docker Compose, one container per robot

## Phase P2 — SAMVAAD Mesh (0/7)
- [ ] T-P2-01 — Transport abstraction (Transport ABC)
- [ ] T-P2-02 — Zenoh peer-mode transport
- [ ] T-P2-03 — UDP multicast fallback transport
- [ ] T-P2-04 — In-process transport (for fast benchmarking)
- [ ] T-P2-05 — Message types
- [ ] T-P2-06 — Range-limited radio + packet-loss/latency model
- [ ] T-P2-07 — Kill the central process — fleet keeps running

## Phase P3 — Deadlock & Conflict Resolution (0/6)
- [ ] T-P3-01 — Wait-for graph builder from peer intents
- [ ] T-P3-02 — Cycle detection (Tarjan SCC)
- [ ] T-P3-03 — Reverse-and-yield recovery manoeuvre
- [ ] T-P3-04 — PIBT priority inheritance with backtracking
- [ ] T-P3-05 — Chaos C1 — head-on single-width aisle
- [ ] T-P3-06 — Chaos C2 — 4-way junction deadlock

## Phase P4 — Task Allocation (0/6)
- [ ] T-P4-01 — Task model + lifecycle states
- [ ] T-P4-02 — Local bid function
- [ ] T-P4-03 — Contract Net auction protocol
- [ ] T-P4-04 — Battery manager — reserve-aware docking
- [ ] T-P4-05 — Chaos C6 — robot dies mid-task, task re-auctioned
- [ ] T-P4-06 — Chaos C7 — battery brownout re-assignment

## Phase P5 — Baseline & First Benchmark (0/5)
- [ ] T-P5-01 — Centralized dispatcher (the SPOF strawman)
- [ ] T-P5-02 — Stop-and-wait conflict handling
- [ ] T-P5-03 — Hungarian-algorithm task assignment
- [ ] T-P5-04 — KASOTI benchmark runner (A/B harness)
- [ ] T-P5-05 — First honest number

## Phase P6 — Edge-AI Advisory Layer (0/6)
- [ ] T-P6-01 — Congestion GRU — training data generator
- [ ] T-P6-02 — Train + export congestion GRU to ONNX
- [ ] T-P6-03 — Priority advisor — DecisionTree(max_depth=5)
- [ ] T-P6-04 — Explainability formatter
- [ ] T-P6-05 — Safety-invariant regression test
- [ ] T-P6-06 — ≥20% gate cleared on the fast sim

## Phase P7 — NETRA Dashboard (0/13)
- [ ] T-P7-01 — Design tokens installed (CSS vars + Tailwind config)
- [ ] T-P7-02 — Status rail component
- [ ] T-P7-03 — Pixel-art warehouse canvas (the viewport)
- [ ] T-P7-04 — Intent bubble layer
- [ ] T-P7-05 — Fleet strip (bottom ticker)
- [ ] T-P7-06 — Robot drawer — TERMINAL / BUILD / MESH / TRACES tabs
- [ ] T-P7-07 — TRACES tab — real decision log, not placeholder text
- [ ] T-P7-08 — Junction inspector
- [ ] T-P7-09 — Control rail — pause / e-stop / teleop / drop-obstacle / kill-wifi
- [ ] T-P7-10 — Read-only telemetry tap (never a controller)
- [ ] T-P7-11 — WebSocket gateway
- [ ] T-P7-12 — Radar-sweep moment on autonomy toggle
- [ ] T-P7-13 — Pre-Ship Checklist pass

## Phase P8 — Chaos Suite (remaining scenarios) (0/9)
- [ ] T-P8-01 — C3 — blocked aisle, D* Lite replan
- [ ] T-P8-02 — C4 — Wi-Fi dead zone, LiDAR-only fallback
- [ ] T-P8-03 — C5 — total blackout, safe-mode
- [ ] T-P8-04 — C8 — human actor on the floor
- [ ] T-P8-05 — C9 — choke-point storm (8 robots, 1 junction)
- [ ] T-P8-06 — C11 — 30% packet loss
- [ ] T-P8-07 — C12 — EXPRESS priority pre-emption
- [ ] T-P8-08 — Live A/B toggle in NETRA
- [ ] T-P8-09 — Live AI-advisor OFF toggle

## Phase P9 — Hardware Bridge (0/5)
- [ ] T-P9-01 — ROS 2 bridge node — VYUHA-Core ⟷ ROS topics
- [ ] T-P9-02 — Nav2 params tuned for the target chassis
- [ ] T-P9-03 — rmw_zenoh real-hardware mesh
- [ ] T-P9-04 — Edge compute budget profiling on real Pi 5
- [ ] T-P9-05 — 2–3 physical robots coordinate live

## Phase P10 — Evidence Package (0/5)
- [ ] T-P10-01 — Full 400-run benchmark matrix executed
- [ ] T-P10-02 — KASOTI human-readable report
- [ ] T-P10-03 — Requirement Traceability Matrix filled in
- [ ] T-P10-04 — Demo script written
- [ ] T-P10-05 — Session replay works end-to-end

## Backlog (non-blocking notes surfaced mid-loop)
"""

for d in directories:
    os.makedirs(d, exist_ok=True)

for f in files:
    with open(f, 'w') as fh:
        pass

with open('PROGRESS.md', 'w') as f:
    f.write(progress_content)

print("Created 39 files/folders. Skeleton created.")
