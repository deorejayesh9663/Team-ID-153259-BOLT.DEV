# 🛡️ VYUHA
### Edge-AI Based Distributed Fleet Coordination for Autonomous Mobile Robots (AMRs) in Smart Warehouses

> **व्यूह (Vyuha)** — an ancient battle formation in which every unit knows its role, holds its position, and yields or advances **without a commander shouting orders**. That is exactly what this system does for a robot fleet.

---

| Field | Value |
|---|---|
| **Problem Statement ID** | **SIH26123** |
| **Organization** | Bharat Electronics Limited (BEL) |
| **Department** | Bharat Electronics Limited |
| **Category** | Software |
| **Theme** | Robotics and Drones / Smart Automation |
| **Event** | Smart India Hackathon 2026 |
| **Team Lead** | Jayesh Deore — TE AI & DS, ADYPSOE, Pune (SPPU) |

---

## 📋 Table of Contents

1. [Problem Statement (Official)](#1-problem-statement-official)
2. [Requirement Traceability Matrix](#2-requirement-traceability-matrix)
3. [Our Solution — VYUHA](#3-our-solution--vyuha)
4. [Design Inspiration & Adaptation](#4-design-inspiration--adaptation)
5. [System Architecture](#5-system-architecture)
6. [Subsystem Breakdown](#6-subsystem-breakdown)
7. [Complete Workflow](#7-complete-workflow)
8. [Algorithms & Decision Logic](#8-algorithms--decision-logic)
9. [The Digital Twin Dashboard (NETRA)](#9-the-digital-twin-dashboard-netra)
10. [Failure & Chaos Scenarios](#10-failure--chaos-scenarios)
11. [Benchmarking & Success Criteria](#11-benchmarking--success-criteria)
12. [Repository Structure](#12-repository-structure)
13. [Development Roadmap](#13-development-roadmap)
14. [Competitive Differentiators](#14-competitive-differentiators)
15. [Hardware Deployment Path](#15-hardware-deployment-path)

---

## 1. Problem Statement (Official)

### 1.1 Background

Modern smart warehouses rely on fleets of **Autonomous Mobile Robots (AMRs)** to move goods efficiently. As fleet sizes grow, relying entirely on a **centralized cloud server** for path planning introduces:

| Issue | Consequence |
|---|---|
| ❌ **High network latency** | Robots wait for the server before every move |
| ❌ **Wi-Fi dead zones** | Robots go blind behind steel racking (RF multipath) |
| ❌ **Single point of failure (SPOF)** | Server dies → entire facility halts |
| ❌ **Delayed real-time decisions** | Cannot react to a human or a fallen pallet in 200 ms |

Modern robotics is therefore shifting toward **decentralized, edge-computing solutions**, where robots communicate **directly with each other** and make **split-second decisions locally**.

### 1.2 Objective

> Design a **decentralized coordination and collision-avoidance framework** for a multi-robot fleet of **at least 3 AMRs** operating in a **dynamic warehouse environment**, running **locally on edge hardware** (Raspberry Pi / Jetson Nano) onboard each robot.

### 1.3 Core Requirements

#### ① Decentralized Communication
Robots must be able to:
- Share their **current position**
- Communicate **intended paths / movements**
- Exchange **localization information**
- Operate **without a central server**

#### ② Dynamic Multi-Agent Conflict Resolution
Resolve in real time:
- **Deadlocks**
- **Potential collisions**
- **Narrow intersections**
- **Warehouse choke points**
- **Overlapping paths**

#### ③ Task Allocation & Re-routing
When the environment changes (e.g. a blocked aisle), the system must:
- **Re-route** the affected robot
- **Change its path**
- **Re-assign pickup points** when necessary
- **Coordinate the remaining fleet** accordingly

### 1.4 Expected Deliverables

| Deliverable | Description |
|---|---|
| **Multi-robot simulation** | Demonstrating decentralized coordination between AMRs |
| **Decentralized network stack** | P2P protocol sharing position, localization, movement intent — no central server for core coordination |
| **Multi-agent path planning** | Edge-capable algorithms accounting for other robots, dynamic obstacles, conflicting paths, deadlocks, narrow passages |
| **Fleet dashboard** | Lightweight real-time monitoring of robot positions, fleet activity, battery status |

### 1.5 Success Criteria (Hard Gates)

> 🎯 **1. ZERO inter-robot collisions**
> 🎯 **2. ≥ 20% reduction in total task completion time** vs. traditional **stop-and-wait** methods on overlapping paths

---

## 2. Requirement Traceability Matrix

Every single requirement above is mapped to a concrete module and a measurable test. **This table is our answer sheet for the judges.**

| # | Requirement | VYUHA Module | Evidence / Test |
|---|---|---|---|
| R1 | Share current position | `SAMVAAD → POSE` broadcast @ 10 Hz | `test_pose_propagation.py` |
| R2 | Communicate intended path | `SAMVAAD → INTENT` (N-step lookahead) | `test_intent_horizon.py` |
| R3 | Exchange localization info | `SAMVAAD → LOCALIZE` (pose + covariance) | `test_covariance_merge.py` |
| R4 | No central server dependency | Zenoh **peer mode**, zero brokers | `test_kill_all_servers.py` |
| R5 | Resolve deadlocks | Wait-for-graph cycle detection + priority recovery | `test_deadlock_4way.py` |
| R6 | Prevent collisions | Space-time reservation table (vertex + edge) | `test_zero_collisions.py` |
| R7 | Narrow intersections | Junction token / mutex cell lock | `test_single_width_aisle.py` |
| R8 | Choke point handling | Congestion-cost inflation on A* | `test_chokepoint_flow.py` |
| R9 | Overlapping paths | PIBT priority inheritance + backtracking | `test_head_on_swap.py` |
| R10 | Blocked aisle → re-route | `BLOCKED` gossip + D* Lite incremental replan | `test_dynamic_obstacle.py` |
| R11 | Re-assign pickup points | Contract Net re-auction on task release | `test_task_reassignment.py` |
| R12 | Fleet re-coordination | Global intent invalidation + cascade replan | `test_cascade_replan.py` |
| R13 | Runs on edge hardware | CPU/RAM profile on Pi 5 class budget | `bench_edge_profile.py` |
| R14 | Dashboard — positions | NETRA live warehouse twin | Visual + screenshot evidence |
| R15 | Dashboard — fleet activity | NETRA fleet strip + event log | Visual + screenshot evidence |
| R16 | Dashboard — battery | NETRA battery ring per AMR | Visual + screenshot evidence |
| R17 | ≥3 AMRs | Configurable `fleet_size` (tested 3 / 4 / 6 / 8 / 12) | `bench_scaling.py` |
| R18 | Dynamic environment | Runtime obstacle injection, human actors | `test_chaos_suite.py` |
| **S1** | **Zero collisions** | Deterministic arbiter + physical occupancy assert | `KASOTI` benchmark report |
| **S2** | **≥20% faster than stop-and-wait** | Baseline vs. VYUHA A/B harness | `KASOTI` benchmark report |

---

## 3. Our Solution — VYUHA

### 3.1 One-Line Pitch

> **VYUHA turns every warehouse robot into its own fleet manager.** No central brain, no server to kill, no Wi-Fi dead zone that stops the floor — and every single decision a robot makes is visible, explainable, and replayable on a live pixel-art digital twin.

### 3.2 The Four Named Subsystems

| Subsystem | Sanskrit | Role |
|---|---|---|
| 🧠 **VYUHA-Core** | व्यूह — formation | The edge autonomy runtime that runs **onboard each AMR** |
| 📡 **SAMVAAD** | संवाद — dialogue | The decentralized peer-to-peer mesh protocol between robots |
| 👁️ **NETRA** | नेत्र — eye | The pixel-art digital twin + per-robot observability dashboard |
| ⚖️ **KASOTI** | कसौटी — touchstone | The benchmark harness that proves both success criteria |

### 3.3 Core Philosophy — The Three Non-Negotiables

#### 🔒 1. Safety is Deterministic, Never Learned
> AI **advises**. Rules **decide**.

The learned layer (congestion predictor, priority advisor) can only **re-rank among already-safe options**. It can **never** authorise a move the deterministic arbiter has refused.

**Why this matters:** BEL is a defence PSU. Black-box neural nets fail safety certification. Current MAPF research (2026) also shows learned methods have **not** proven superior to search-based methods. A 100% auditable right-of-way protocol is both safer *and* research-aligned.

#### 👁️ 2. Every Decision is Explainable
Click any robot at any moment → see **exactly why** it yielded, what it predicted, who it negotiated with, and what the alternatives cost. No "the robot just stopped."

#### 💀 3. Graceful Degradation, Never Cliff-Edge Failure
```
Full mesh  →  Partial mesh  →  Neighbours only  →  Total blackout
   ▼              ▼                  ▼                    ▼
Optimal      Conservative       Local-only          LiDAR-only
planning     reservations       negotiation      reactive safe-mode
                                                 (slow but collision-free)
```
The fleet **never** stops entirely. It gets slower, not dead.

---

## 4. Design Inspiration & Adaptation

This project's **interface and observability model** is adapted from a multi-agent AI simulation pattern: a **2D pixel-art world** where each autonomous agent is independently spawned, configured, and monitored through a per-agent control panel with live terminal, message log, and decision traces.

We port that **exact interaction model** from an office of AI workers to a **warehouse of AI robots**:

| Original Pattern (AI Office Sim) | VYUHA Adaptation (AMR Warehouse) |
|---|---|
| Pixel-art office floor plan | 🏭 **Pixel-art warehouse**: aisles, racks, pick stations, dock doors, charging bays |
| Characters (Michael, Jim, Pam…) | 🤖 **AMR units** (AMR-01 … AMR-12) with unique livery colours |
| Agent Creation: Identity / Workspace / Engine / Briefing | 🛠️ **Robot Commissioning**: Identity / Zone / Edge Engine / Mission Brief |
| Speech bubbles with dialogue | 💬 **Intent bubbles**: `yielding to AMR-03`, `reserving A4:t+3`, `battery 18% → dock`, `aisle B2 blocked` |
| `TERMINAL` tab (live process output) | 📟 **TERMINAL** — live ROS 2 / autonomy node log from that robot |
| `GIT` tab | 🔖 **BUILD** — firmware hash, config version, last OTA |
| `MESSAGES` tab | 📡 **MESH** — every SAMVAAD packet sent/received by that robot |
| `TRACES` tab (reasoning chain) | 🧾 **TRACES** — the full decision trace: *why* it yielded, cost breakdown, alternatives rejected |
| `pause` / `kill` / `steer` | ⏸️ **pause** / 🛑 **e-stop** / 🕹️ **teleop override** |
| `auto mode on` | 🟢 **AUTONOMY: ON** — fleet runs with zero operator input |
| Agent strip at bottom of screen | 🔋 **Fleet strip** — every AMR with live battery, state, current task |
| Load agent from `.json` manifest | 📄 Load fleet from `fleet_config.json` |
| "Create one with AI…" | ✨ "Generate a stress scenario with AI…" |

> **Why this matters for judging:** Most SIH teams will present a matplotlib grid with coloured squares. We present a **living warehouse you can click into** — and behind the pixel art sits a rigorous, benchmarked, auditable protocol. The demo sells itself in 15 seconds; the traceability matrix wins the technical round.

---

## 5. System Architecture

### 5.1 Layered View

```
╔══════════════════════════════════════════════════════════════════════╗
║  L5  ⚖️  KASOTI — BENCHMARK & EVIDENCE HARNESS                       ║
║      Baseline (stop-and-wait)  ⟷  VYUHA   |  Collisions · Makespan   ║
║      Throughput · Deadlocks · Msgs/s · Energy  →  PASS / FAIL report ║
╠══════════════════════════════════════════════════════════════════════╣
║  L4  👁️  NETRA — DIGITAL TWIN & OBSERVABILITY  (operator laptop)     ║
║      Pixel warehouse · Intent bubbles · Per-robot panel              ║
║      TERMINAL | BUILD | MESH | TRACES     ⏸ pause  🛑 e-stop  🕹 teleop ║
║      ⚠️ READ-ONLY OBSERVER — kill it and the fleet keeps running     ║
╠══════════════════════════════════════════════════════════════════════╣
║  L3  📡  SAMVAAD — DECENTRALIZED P2P MESH  (no broker, no server)    ║
║      Zenoh peer-mode  ·  UDP-multicast fallback                      ║
║      HEARTBEAT · POSE · INTENT · RESERVE · YIELD · BID · BLOCKED     ║
║      Range-limited radio model · Gossip propagation · CRDT merge     ║
╠══════════════════════════════════════════════════════════════════════╣
║  L2  🧠  VYUHA-CORE — EDGE DECISION BRAIN  (runs ON EACH ROBOT)      ║
║  ┌────────────────────────────────────────────────────────────────┐ ║
║  │ Belief State  │ Global Planner │ Reservation │ Conflict         │ ║
║  │ (world model) │ A* / D* Lite   │   Table     │  Arbiter ⚖️      │ ║
║  ├───────────────┼────────────────┼─────────────┼──────────────────┤ ║
║  │ Task Bidder   │ Edge-AI Advisor│  Deadlock   │ Battery /        │ ║
║  │ (Contract Net)│ (TinyML, ADVISE)│  Resolver  │ Charge Manager   │ ║
║  └────────────────────────────────────────────────────────────────┘ ║
╠══════════════════════════════════════════════════════════════════════╣
║  L1  🦾  LOCAL AUTONOMY  (ROS 2 + Nav2)                              ║
║      AMCL / SLAM · Local costmap · DWB controller · Recovery         ║
║      ORCA velocity obstacles · Emergency stop reflex                 ║
╠══════════════════════════════════════════════════════════════════════╣
║  L0  🔌  EDGE HARDWARE  (per robot)                                  ║
║      Raspberry Pi 5 / Jetson Orin Nano · 2D LiDAR · IMU · Encoders   ║
║      Differential drive · Battery BMS · Wi-Fi 6 radio                ║
╚══════════════════════════════════════════════════════════════════════╝
```

### 5.2 The Critical Architectural Claim

```
            ❌ TRADITIONAL (Centralized)          ✅ VYUHA (Decentralized)

                  ┌─────────┐                    ┌────┐◄──►┌────┐◄──►┌────┐
                  │ CLOUD   │                    │AMR1│    │AMR2│    │AMR3│
                  │ SERVER  │  ← SPOF            └─┬──┘    └─┬──┘    └─┬──┘
                  └────┬────┘                      │  ╲    ╱ │ ╲     ╱ │
             ┌─────────┼─────────┐                 │   ╲  ╱  │  ╲   ╱  │
          ┌──┴──┐   ┌──┴──┐   ┌──┴──┐              │    ╲╱   │   ╲ ╱   │
          │AMR1 │   │AMR2 │   │AMR3 │            ┌─┴──┐ ╱╲ ┌─┴──┐ ╱╲┌──┴─┐
          └─────┘   └─────┘   └─────┘            │AMR4│◄──►│AMR5│◄──►│AMR6│
                                                 └────┘    └────┘    └────┘
          Server dies → floor stops              Any robot dies → fleet adapts
          Wi-Fi drop  → robot blind              Wi-Fi drop  → LiDAR safe-mode
          Latency     → server round-trip        Latency     → local, <50 ms
```

> 🔑 **NETRA (the dashboard) is a passive observer, not a controller.** Unplug the operator laptop mid-demo and the fleet continues working. *This single live demo moment proves the entire thesis of the problem statement.*

---

## 6. Subsystem Breakdown

### 6.1 🧠 VYUHA-Core — The Edge Brain

Runs as an independent process **on every robot**. Contains no reference to any other robot's internal state — only what arrives over the mesh.

| Component | Responsibility |
|---|---|
| **Belief State** | Robot's private world model: own pose, known peers, occupancy grid, blocked cells, reservation ledger |
| **Global Planner** | Grid A* with congestion-inflated costs; **D* Lite** for incremental replan when a cell is blocked |
| **Reservation Table** | Space-time claims: `(cell, t_start, t_end)` for vertices and `(edgeA→B, t)` for edges |
| **Conflict Arbiter** ⚖️ | Deterministic right-of-way: **priority weight → remaining distance → lexicographic robot ID**. Total order ⇒ mathematically deadlock-free |
| **Edge-AI Advisor** | TinyML congestion forecaster (+5 s occupancy) + explainable priority advisor (`DecisionTree`, `max_depth=5`) — **advisory only** |
| **Deadlock Resolver** | Builds wait-for graph; on cycle detection, lowest-priority member executes a reverse-and-yield manoeuvre |
| **Task Bidder** | Contract Net Protocol — computes local bid from distance, battery, load, predicted congestion |
| **Battery Manager** | Reserve-aware: releases claimed tasks and docks when SoC drops below the return-threshold |

### 6.2 📡 SAMVAAD — The Mesh Protocol

**Transport:** Eclipse **Zenoh** in **peer mode** — no broker, no router, true P2P.
**Fallback:** UDP multicast backend for hosts without Zenoh.
**Rationale:** Published ROS 2 middleware benchmarks show Zenoh outperforms CycloneDDS and MQTT **over Wi-Fi** and produced the smallest real-robot trajectory drift — exactly the warehouse condition the PS describes.

#### Message Types

| Type | Rate | Payload | Purpose |
|---|---|---|---|
| `HEARTBEAT` | 2 Hz | id, state, battery, uptime | Liveness; missed beats ⇒ peer presumed dead |
| `POSE` | 10 Hz | x, y, θ, v, ω, covariance | **R1** — current position |
| `LOCALIZE` | 1 Hz | AMCL covariance, landmark fixes | **R3** — shared localization |
| `INTENT` | On replan | Next N cells + arrival time windows | **R2** — declared future path |
| `RESERVE` | On claim | (cell, t_start, t_end), priority | Space-time claim |
| `YIELD` | On conflict | target_id, reason_code, duration | Explicit right-of-way handover |
| `BID` / `AWARD` | On task | task_id, cost, battery, ETA | **R11** — decentralized auction |
| `BLOCKED` | On detect | cell, confidence, TTL | **R10** — gossip hazard propagation |
| `RELEASE` | On complete | cell list / task_id | Frees reservations |
| `HELP` | On stuck | pose, stuck_duration | Cooperative unblocking |

#### Realism Features
- **Simulated radio range** (configurable, e.g. 18 m) — robots genuinely cannot hear the far side of the warehouse
- **Packet loss & latency injection** — proves robustness, not luck
- **Vector-clock / CRDT merge** — conflicting reservation views converge without a coordinator
- **TTL-based gossip** — a `BLOCKED` report spreads robot-to-robot across the floor

### 6.3 👁️ NETRA — Digital Twin Dashboard

See [Section 9](#9-the-digital-twin-dashboard-netra) for the full specification.

### 6.4 ⚖️ KASOTI — Benchmark Harness

See [Section 11](#11-benchmarking--success-criteria).

---

## 7. Complete Workflow

### 7.1 Robot Commissioning Flow

```
┌───────────────────────────────────────────────────────────────┐
│               🛠️  COMMISSION AN AMR                            │
├───────────────────────────────────────────────────────────────┤
│  ① IDENTITY      robot_id · display name · livery colour       │
│                  chassis class · footprint (L×W) · max speed   │
│                                                               │
│  ② ZONE          home dock · assigned aisles · restricted      │
│                  areas · priority class (STD / EXPRESS / COLD) │
│                                                               │
│  ③ EDGE ENGINE   compute target (Pi 5 / Jetson Orin Nano)      │
│                  planner (A* / D* Lite) · replan horizon       │
│                  AI advisor ON/OFF · radio range · tick rate   │
│                                                               │
│  ④ MISSION BRIEF standing orders · battery return threshold    │
│                  yield policy · max wait before escalation     │
├───────────────────────────────────────────────────────────────┤
│     📄 Load from fleet_config.json     ✨ Generate with AI      │
└───────────────────────────┬───────────────────────────────────┘
                            ▼
                    ROBOT SPAWNS ON FLOOR
                    Joins SAMVAAD mesh
                    Broadcasts first HEARTBEAT
```

### 7.2 The Per-Tick Decision Loop (runs on every robot, ~10 Hz)

```
   ┌──────────────────────────────────────────────────────────────┐
   │ 1. SENSE      LiDAR scan · odometry · IMU · battery SoC       │
   ├──────────────────────────────────────────────────────────────┤
   │ 2. LISTEN     Drain SAMVAAD inbox → update Belief State       │
   │               peer poses · peer intents · reservations        │
   │               blocked-cell gossip · incoming bids             │
   ├──────────────────────────────────────────────────────────────┤
   │ 3. PREDICT    Edge-AI: forecast aisle occupancy at t+5 s      │
   │               → produces a CONGESTION COST MAP (advisory)     │
   ├──────────────────────────────────────────────────────────────┤
   │ 4. PLAN       A* / D* Lite over grid                          │
   │               cost = distance + congestion + priority penalty │
   │               → candidate path P                              │
   ├──────────────────────────────────────────────────────────────┤
   │ 5. CHECK      Test P against the space-time reservation table │
   │               Detect: vertex · edge(head-on) · swap conflicts │
   ├──────────────────────────────────────────────────────────────┤
   │ 6. ARBITRATE ⚖️ DETERMINISTIC — CANNOT BE OVERRIDDEN BY AI     │
   │      Conflict? → compare (priority_weight,                    │
   │                           remaining_distance,                 │
   │                           robot_id)                           │
   │      WIN  → RESERVE cells, broadcast INTENT, proceed          │
   │      LOSE → YIELD (hold / sidestep / reverse into bay)        │
   │      Log the full reasoning into TRACES                       │
   ├──────────────────────────────────────────────────────────────┤
   │ 7. DEADLOCK?  Build wait-for graph from peer intents          │
   │               Cycle found → lowest-priority member backs off  │
   ├──────────────────────────────────────────────────────────────┤
   │ 8. ACT        Publish velocity cmd → Nav2 / ORCA local ctrl   │
   │               Emergency-stop reflex overrides everything      │
   ├──────────────────────────────────────────────────────────────┤
   │ 9. BROADCAST  POSE · INTENT · RESERVE · any BLOCKED discovery │
   ├──────────────────────────────────────────────────────────────┤
   │ 10. EMIT      Structured trace event → NETRA (fire-and-forget)│
   └───────────────────────┬──────────────────────────────────────┘
                           └──────────► repeat
```

### 7.3 Task Lifecycle (Decentralized Auction)

```
 📦 Task appears at pick station (TASK-0451, priority EXPRESS)
              │
              ▼
 📡 ANNOUNCE broadcast on SAMVAAD to all in-range robots
              │
      ┌───────┴────────┬────────────────┐
      ▼                ▼                ▼
   AMR-02           AMR-05           AMR-07
   computes bid     computes bid     computes bid
   locally          locally          locally
      │                │                │
   cost = w₁·path_len + w₂·(1/battery) + w₃·congestion
        + w₄·current_load + w₅·priority_match
      │                │                │
      └───────┬────────┴────────────────┘
              ▼
 🏆 LOWEST BID WINS  (ties → lexicographic robot_id, deterministic)
              │
              ▼
 ✅ Winner broadcasts CLAIM → peers ACK → task locked
              │
              ▼
 🚚 Execute: dock → pick → transit → drop → RELEASE
              │
   ┌──────────┴──────────────────────────┐
   ▼                                     ▼
 ✅ Success                     ⚠️ Aisle blocked mid-route
   RELEASE + metrics                     │
                              ┌──────────┴──────────┐
                              ▼                     ▼
                     Reroute possible?      Battery too low /
                     → D* Lite replan        no viable path?
                     → new INTENT            → RELEASE task
                                             → RE-AUCTION to fleet
                                             → R11 + R12 satisfied ✅
```

---

## 8. Algorithms & Decision Logic

### 8.1 Algorithm Selection & Justification

| Layer | Algorithm | Why This One |
|---|---|---|
| **Single-agent path** | **A\*** with congestion-inflated cost | O(ms) on Pi-class CPU; admissible heuristic; well-understood |
| **Incremental replan** | **D\* Lite** | Reuses previous search tree — replanning a blocked aisle costs a fraction of a full A* |
| **Multi-agent (fleet)** | **Prioritized Planning + PIBT-style priority inheritance with backtracking** | 2026 warehouse-MAPF benchmarking shows PP and LNS2 struggle as agent count rises, while **PIBT-based approaches achieve preferable scalability** — and PIBT is cheap enough to run on edge hardware |
| **Conflict guarantee** | **Space-time reservation table** (vertex + edge) | Catches head-on and swap conflicts that pure spatial checks miss |
| **Local avoidance** | **ORCA** (velocity obstacles) | Smooth continuous-space avoidance under the discrete plan |
| **Deadlock** | **Wait-for graph cycle detection** + priority-based recovery | Detection is provable, not heuristic |
| **Task allocation** | **Contract Net Protocol** (decentralized auction) | No auctioneer needed; degrades naturally with radio range |
| **Baseline comparison** | **Hungarian algorithm** + centralized stop-and-wait | The thing we must beat by ≥20% |
| **Edge-AI advisory** | **DecisionTree (depth ≤ 5)** + lightweight GRU occupancy forecaster | Explainable, <1 MB, microsecond inference, certifiable |

### 8.2 The Deterministic Right-of-Way Protocol

When two robots claim overlapping space-time:

```python
def arbitrate(self, peer) -> Decision:
    """
    Total ordering over (priority, distance, id) guarantees:
      • Antisymmetric  → exactly one robot wins
      • Transitive     → no cyclic precedence
      ⇒ MATHEMATICALLY DEADLOCK-FREE
    """
    # Tier 1 — mission priority (EXPRESS > STANDARD > IDLE)
    #          the AI advisor may adjust ONLY this weight,
    #          and ONLY among already-safe alternatives
    if self.priority_weight != peer.priority_weight:
        return WIN if self.priority_weight > peer.priority_weight else YIELD

    # Tier 2 — the robot closer to finishing clears the aisle faster
    if self.remaining_distance != peer.remaining_distance:
        return WIN if self.remaining_distance < peer.remaining_distance else YIELD

    # Tier 3 — deterministic, symmetric-safe tie-break
    return WIN if self.robot_id < peer.robot_id else YIELD
```

### 8.3 The Safety Invariant (the line we never cross)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   🧠 LEARNED LAYER (advisory)      ⚖️ DETERMINISTIC LAYER        │
│   ─────────────────────────       ──────────────────────        │
│   • congestion forecast           • reservation table            │
│   • priority re-ranking           • right-of-way protocol        │
│   • route preference              • physical occupancy assert    │
│   • ETA estimation                • emergency-stop reflex        │
│                                                                 │
│         ▼                                   ▼                   │
│   "I SUGGEST aisle C is                "I DECIDE whether        │
│    about to jam — prefer D"             the move is legal"      │
│                                                                 │
│   ╔═══════════════════════════════════════════════════════════╗ │
│   ║  INVARIANT: The learned layer can only re-rank among      ║ │
│   ║  alternatives the deterministic layer has ALREADY         ║ │
│   ║  certified as collision-free. It can never create,        ║ │
│   ║  approve, or unlock an unsafe move.                       ║ │
│   ║                                                           ║ │
│   ║  ⇒ Turn the AI completely OFF and the fleet is still      ║ │
│   ║    100% collision-free — only slower.                     ║ │
│   ╚═══════════════════════════════════════════════════════════╝ │
└─────────────────────────────────────────────────────────────────┘
```

> 🎤 **Demo moment:** toggle `AI Advisor: OFF` live. Collisions stay at **0**; throughput drops ~12%. That single toggle proves the AI is an optimizer, not a crutch — exactly what a defence customer needs to hear.

---

## 9. The Digital Twin Dashboard (NETRA)

### 9.1 Warehouse Floor Layout

```
┌────────────────────────────────────────────────────────────────────┐
│ 🕐 08:42:17   AUTONOMY ● ON   MESH ● 6/6   COLLISIONS 0   ⏸ 🛑 🕹  │
├────────────────────────────────────────────────────────────────────┤
│  ╔═ INBOUND DOCK ═╗                          ╔═ OUTBOUND DOCK ═╗   │
│  ║ 🚪  🚪  🚪      ║                          ║      🚪  🚪  🚪  ║   │
│  ╚════════════════╝                          ╚═════════════════╝   │
│                                                                    │
│   A1 ▓▓▓▓▓▓▓▓  🤖①→        A2 ▓▓▓▓▓▓▓▓        A3 ▓▓▓▓▓▓▓▓         │
│   ────────────  ╭──────────────────╮  ──────────────────────       │
│   B1 ▓▓▓▓▓▓▓▓   │ reserving A2:t+3 │   B3 ▓▓▓▓▓▓▓▓                 │
│   ────────────  ╰────────┬─────────╯  ───────────────────          │
│   C1 ▓▓▓▓▓▓▓▓      ◆JUNCTION     🤖③   C3 ▓▓▓▓▓▓▓▓                 │
│   ────────────    ╭──────────────╮  ─────────────────────          │
│   D1 ▓▓▓▓▓▓▓▓  🤖② │ yielding to ① │   D3 ▓▓▓▓▓▓ ✖ BLOCKED         │
│   ────────────    ╰──────────────╯  ─────────────────────          │
│                                            🤖④ ↻ rerouting          │
│  ╔═ PICK STATIONS ═╗   ⚡ CHARGE BAYS ⚡                            │
│  ║ P1  P2  P3  P4  ║   🔌🤖⑤ 43%▲   🔌 ---                          │
│  ╚═════════════════╝                                               │
├────────────────────────────────────────────────────────────────────┤
│ 🔋 FLEET STRIP                                                     │
│ ①AMR-01 87%▮▮▮▮ TRANSIT  │ ②AMR-02 62%▮▮▮ YIELD  │ ③AMR-03 91% PICK│
│ ④AMR-04 55%▮▮ REROUTE    │ ⑤AMR-05 43%▮ CHARGE   │ ⑥AMR-06 78% IDLE│
└────────────────────────────────────────────────────────────────────┘

Legend:  ▓ rack   ◆ junction/choke point   ✖ blocked   → heading
         ╭─╮ live intent bubble            ⚡ charging bay
```

### 9.2 Per-Robot Inspection Panel

Click any robot → a side panel opens (directly mirroring the original pattern):

```
┌───────────────────────────────────────────────────────┐
│ 🤖 AMR-03      ● ACTIVE          Zone: A-Block         │
│ Edge: Jetson Orin Nano · CPU 34% · RAM 512MB · 12ms    │
├───────────────────────────────────────────────────────┤
│ CONTROL   ⏸ pause   🛑 e-stop   🕹 teleop   ↻ replan   │
│ ⚠ Injected as an operator hint. The robot's           │
│   deterministic arbiter still has final authority.    │
├───────────────────────────────────────────────────────┤
│ 📟 TERMINAL │ 🔖 BUILD │ 📡 MESH │ 🧾 TRACES           │
├───────────────────────────────────────────────────────┤
│ 🧾 TRACES — why AMR-03 yielded at t=08:42:09          │
│                                                       │
│  ▸ CONFLICT  vertex (14,7) @ t+2.4s  with AMR-01      │
│  ▸ TIER 1    priority  STD(1.0) vs EXPRESS(2.5)       │
│              → AMR-01 outranks                        │
│  ▸ DECISION  YIELD  ·  hold 3.1s  ·  reason RW_PRIO   │
│  ▸ AI ADVICE congestion(A2, t+5s) = 0.71 HIGH         │
│              suggested alt-route via C — cost +8.2m   │
│              ⚠ ADVISORY ONLY — not used for safety    │
│  ▸ ALT       reverse-into-bay = +6.8s (rejected)      │
│  ▸ COST      yield 3.1s  <  reroute 8.2s  ✅          │
├───────────────────────────────────────────────────────┤
│ ⏱ QUEUE  TASK-0451 (EXPRESS) → TASK-0467 → TASK-0470  │
│ 🔋 91%  ·  est. 2h14m remaining  ·  dock B in 14 tasks│
└───────────────────────────────────────────────────────┘
```

### 9.3 Junction Inspector

Click any **◆ junction cell**:

| Field | Example |
|---|---|
| Current occupancy | `AMR-01` |
| Predicted occupancy (+5 s) | `0.71 — HIGH` |
| Active reservations | `AMR-01 [t+0 → t+2.4]`, `AMR-03 [t+3.1 → t+5.0]` |
| Queue | `AMR-03`, `AMR-06` |
| Conflicts resolved here (session) | `47` |
| Predictor kind | `GRU-lite · 8.3 KB · 0.4 ms inference` |

### 9.4 Operator Control Rail

| Control | Effect | What It Proves |
|---|---|---|
| ⏸ **Pause fleet** | Global soft-stop | Safe human intervention |
| 🛑 **E-stop AMR-n** | Immediate halt of one unit | **Fleet re-plans around a dead robot** |
| 🕹 **Teleop override** | Manual drive one AMR | Human-in-the-loop coexistence |
| 📦 **Drop obstacle** | Place a pallet in any aisle | **R10** live re-route |
| 🚫 **Kill Wi-Fi zone** | Blackout a map region | **Graceful degradation** |
| 💀 **Kill NETRA** | Close the dashboard | **Fleet keeps running — no SPOF** ⭐ |
| 🔀 **A/B toggle** | Baseline ⟷ VYUHA | **Live proof of the ≥20% gain** ⭐ |
| 🧠 **AI Advisor toggle** | Learned layer on/off | **Collisions stay 0 either way** ⭐ |
| ⏪ **Replay** | Scrub a recorded session | Post-incident forensics |

---

## 10. Failure & Chaos Scenarios

Every scenario below is a scripted, repeatable test **and** a 20-second demo beat.

| # | Scenario | Trigger | Expected VYUHA Behaviour |
|---|---|---|---|
| **C1** | **Head-on in a single-width aisle** | Two AMRs, opposite ends of aisle B2 | Lower-priority reverses into the nearest passing bay; higher passes; both resume. **Zero contact.** |
| **C2** | **4-way junction deadlock** | 4 AMRs arrive simultaneously at a cross | Wait-for graph detects the cycle; lowest-priority backs off; clockwise release. **Resolved in <2 s.** |
| **C3** | **Blocked aisle** | Operator drops a pallet in D3 | Discovering robot gossips `BLOCKED`; D* Lite replans; **fleet-wide cost map updates via peer relay** |
| **C4** | **Wi-Fi dead zone** | Kill radio in the rear quadrant | Robots inside fall back to LiDAR-only reactive mode, drive conservatively, **re-sync on exit** |
| **C5** | **Total network blackout** | Kill the entire mesh | All robots enter safe-mode: reduced speed, enlarged clearance. **Still zero collisions.** |
| **C6** | **Robot failure mid-task** | E-stop AMR-04 while carrying a load | Peers stop hearing `HEARTBEAT` → mark dead → **its reservations expire (TTL) → task re-auctioned** |
| **C7** | **Battery brownout** | Force SoC to 12% | Robot releases its claimed task, broadcasts `RELEASE`, docks; **task re-auctioned to a healthy peer** |
| **C8** | **Human on the floor** | Spawn a walking human actor | All robots in LOS treat it as a dynamic high-clearance obstacle and re-route |
| **C9** | **Choke-point storm** | Route 8 AMRs through one junction | Congestion predictor pre-emptively spreads traffic; **throughput degrades gracefully, never deadlocks** |
| **C10** | **Dashboard death** | Close NETRA entirely | ⭐ **Absolutely nothing changes on the floor.** |
| **C11** | **Packet loss 30%** | Inject lossy radio | Reservations still converge via CRDT merge; robots become more conservative |
| **C12** | **Priority pre-emption** | Inject an EXPRESS medical task | All STANDARD units yield the corridor; express route clears |

---

## 11. Benchmarking & Success Criteria

### 11.1 The Two Gates

| Gate | Target | How We Measure |
|---|---|---|
| 🎯 **S1 — Zero collisions** | **0** inter-robot collisions | Physical footprint overlap assertion on **every** simulation tick, accumulated over total robot-hours |
| 🎯 **S2 — ≥20% faster** | **≥20%** reduction in total task completion time | Identical task sets + identical seeds, run against a centralized **stop-and-wait** baseline |

### 11.2 Experimental Design

```
FIXED:    warehouse map · task set · random seed · robot kinematics
VARIED:   coordination strategy  ∈  { BASELINE_STOP_AND_WAIT, VYUHA }
          fleet size             ∈  { 3, 4, 6, 8, 12 }
          task count             ∈  { 20, 50, 100, 200 }
          seeds                  ∈  { 42 … 51 }   (10 repetitions)

⇒ 2 × 5 × 4 × 10 = 400 runs per full matrix
   Report mean ± 95% CI. Every result reproducible from its seed.
```

### 11.3 Metrics Collected

| Category | Metrics |
|---|---|
| **Safety** ⭐ | Inter-robot collisions · near-miss count · min separation distance · emergency stops |
| **Efficiency** ⭐ | Makespan · mean task completion time · throughput (tasks/hour) · robot utilisation % |
| **Coordination** | Deadlocks detected · deadlocks resolved · mean resolution time · yields issued · replans triggered |
| **Network** | Messages/sec/robot · bandwidth (KB/s) · mean & p99 latency · packets dropped |
| **Edge Compute** | CPU % · RAM MB · planning time p50/p95/p99 · inference latency |
| **Energy** | Distance travelled · idle time · charge cycles · energy per task |

### 11.4 Report Format

```
═══════════════════════════════════════════════════════════════
  KASOTI BENCHMARK REPORT — VYUHA vs STOP-AND-WAIT
  Commit a3f7c21 · 2026-XX-XX · 400 runs · 312.4 robot-hours
═══════════════════════════════════════════════════════════════

  Fleet │  Baseline │    VYUHA │ Improvement │ Collisions │ Gate
  ──────┼───────────┼──────────┼─────────────┼────────────┼──────
    3   │  1284.3 s │  798.1 s │    ▼ 37.9 % │      0     │ PASS
    4   │  1610.7 s │  921.4 s │    ▼ 42.8 % │      0     │ PASS
    6   │  2455.1 s │ 1288.6 s │    ▼ 47.5 % │      0     │ PASS
    8   │  3390.8 s │ 2044.2 s │    ▼ 39.7 % │      0     │ PASS
   12   │  5812.0 s │ 3766.9 s │    ▼ 35.2 % │      0     │ PASS
  ──────┴───────────┴──────────┴─────────────┴────────────┴──────

  S1  ZERO COLLISIONS ................................ ✅ PASS
      0 collisions across 312.4 robot-hours
  S2  ≥20% TASK-TIME REDUCTION ....................... ✅ PASS
      Minimum observed improvement: 35.2 % (target 20 %)

  ⚠️  Numbers above are the TARGET/ILLUSTRATIVE format.
      Real figures are emitted by `python -m kasoti.benchmark`.
═══════════════════════════════════════════════════════════════
```

> ⚖️ **Honesty rule we hold ourselves to:** KASOTI reports what it measured on the configurations it ran. We never claim the gates hold for every possible workload — only that they hold, reproducibly, on the documented benchmark matrix. Judges respect measured evidence far more than a round number with no seed behind it.

---

## 12. Repository Structure

```
vyuha/
│
├── 📁 vyuha_core/                    # 🧠 EDGE BRAIN (runs on each robot)
│   ├── belief/
│   │   ├── world_model.py            # private occupancy + peer registry
│   │   ├── peer_registry.py          # liveness, TTL, dead-peer reaping
│   │   └── blocked_cells.py          # gossiped hazard map w/ decay
│   ├── planning/
│   │   ├── astar.py                  # congestion-weighted A*
│   │   ├── dstar_lite.py             # incremental replan
│   │   ├── reservation_table.py      # space-time vertex + edge claims
│   │   ├── pibt.py                   # priority inheritance w/ backtracking
│   │   └── orca.py                   # velocity-obstacle local avoidance
│   ├── arbitration/
│   │   ├── conflict_arbiter.py       # ⚖️ DETERMINISTIC right-of-way
│   │   ├── deadlock_detector.py      # wait-for graph cycle detection
│   │   └── recovery.py               # reverse-and-yield manoeuvres
│   ├── edge_ai/
│   │   ├── congestion_gru.py         # occupancy forecast +5s
│   │   ├── priority_advisor.py       # DecisionTree(max_depth=5)
│   │   ├── explain.py                # human-readable rationale
│   │   └── models/                   # exported .onnx / .tflite
│   ├── tasks/
│   │   ├── contract_net.py           # decentralized auction
│   │   ├── bid_function.py           # local cost computation
│   │   └── task_model.py
│   ├── power/
│   │   └── battery_manager.py        # reserve-aware docking
│   └── runtime.py                    # the 10 Hz decision loop
│
├── 📁 samvaad/                       # 📡 P2P MESH PROTOCOL
│   ├── transport/
│   │   ├── zenoh_peer.py             # primary — broker-free
│   │   └── udp_multicast.py          # fallback backend
│   ├── messages.py                   # POSE, INTENT, RESERVE, BID, …
│   ├── gossip.py                     # TTL flood for BLOCKED
│   ├── crdt_merge.py                 # conflict-free state convergence
│   ├── radio_model.py                # range · loss · latency simulation
│   └── security.py                   # message signing / replay guard
│
├── 📁 netra/                         # 👁️ DIGITAL TWIN DASHBOARD
│   ├── web/
│   │   ├── warehouse_canvas.jsx      # pixel-art floor renderer
│   │   ├── intent_bubbles.jsx        # live speech-bubble layer
│   │   ├── robot_panel.jsx           # TERMINAL | BUILD | MESH | TRACES
│   │   ├── junction_inspector.jsx
│   │   ├── fleet_strip.jsx           # bottom battery/status rail
│   │   └── control_rail.jsx          # pause · e-stop · chaos buttons
│   ├── server/
│   │   ├── telemetry_sink.py         # ⚠️ READ-ONLY tap on the mesh
│   │   ├── trace_store.py            # decision traces for replay
│   │   └── ws_gateway.py
│   └── assets/
│       ├── sprites/                  # AMR sprites, racks, pallets, docks
│       └── tiles/
│
├── 📁 sim/                           # 🏭 SIMULATION ENVIRONMENT
│   ├── warehouse.py                  # grid, racks, aisles, docks, bays
│   ├── physics.py                    # kinematics, footprint collision
│   ├── actors.py                     # humans, forklifts, dropped pallets
│   ├── clock.py                      # deterministic tick scheduler
│   └── maps/
│       ├── small_3amr.json
│       ├── medium_6amr.json
│       └── large_12amr.json
│
├── 📁 baseline/                      # ❌ THE THING WE MUST BEAT
│   ├── central_server.py             # classic centralized dispatcher
│   ├── stop_and_wait.py              # traditional halt-on-conflict
│   └── hungarian_assign.py           # centralized optimal assignment
│
├── 📁 kasoti/                        # ⚖️ BENCHMARK HARNESS
│   ├── benchmark.py                  # A/B matrix runner
│   ├── metrics.py                    # all metric collectors
│   ├── report.py                     # human-readable PASS/FAIL report
│   ├── chaos.py                      # C1–C12 scenario injection
│   └── results/
│
├── 📁 ros2_ws/                       # 🦾 REAL-HARDWARE BRIDGE
│   └── src/vyuha_ros/
│       ├── vyuha_bridge_node.py      # VYUHA-Core ⟷ ROS 2 topics
│       ├── nav2_params.yaml
│       └── launch/
│
├── 📁 tests/
│   ├── unit/
│   ├── integration/
│   ├── safety/                       # ⭐ zero-collision invariants
│   └── chaos/                        # ⭐ C1–C12 regression suite
│
├── 📁 docs/
│   ├── PROJECT.md                    # ← this file
│   ├── TECH_STACK.md
│   ├── ARCHITECTURE.md
│   ├── PROTOCOL.md                   # SAMVAAD wire format
│   ├── TRACEABILITY.md               # R1–R18 → code → test
│   └── BENCHMARK.md
│
├── fleet_config.json                 # 📄 the fleet manifest
├── requirements.txt
├── docker-compose.yml                # N robot containers + NETRA
└── README.md
```

---

## 13. Development Roadmap

| Phase | Deliverable | Gate to Pass |
|---|---|---|
| **P0 — Foundation** | Grid warehouse sim, A* planner, 1 robot moving | Robot completes a task solo |
| **P1 — Multi-agent** | 3 robots, reservation table, deterministic arbiter | **Zero collisions, 3 AMRs** ⭐ |
| **P2 — Mesh** | SAMVAAD over Zenoh, range-limited radio, gossip | Kill the central process — fleet survives ⭐ |
| **P3 — Deadlock** | Wait-for graph, PIBT, recovery manoeuvres | C1 + C2 pass repeatably |
| **P4 — Tasks** | Contract Net auction, battery, re-assignment | C6 + C7 pass |
| **P5 — Baseline** | Stop-and-wait implementation + KASOTI harness | First honest A/B number |
| **P6 — Edge-AI** | Congestion GRU + priority advisor + explainability | **≥20% gate cleared** ⭐ |
| **P7 — NETRA** | Pixel warehouse, intent bubbles, robot panel, traces | Full demo runs end-to-end |
| **P8 — Chaos** | C1–C12 scripted, replay, A/B live toggle | All 12 scenarios green |
| **P9 — Hardware** | ROS 2 bridge, 2–3 physical AMRs on Pi/Jetson | Real robots coordinate ⭐ |
| **P10 — Evidence** | Traceability matrix, full benchmark, demo script | Judge-ready package |

---

## 14. Competitive Differentiators

Honest assessment of what separates this from the other teams attacking SIH26123:

| # | Differentiator | Why Judges Care |
|---|---|---|
| 1 | 🎬 **Watchable, clickable digital twin** | Most teams show a matplotlib grid. We show a **living warehouse** the judge can click into. Attention is currency in a 10-minute pitch. |
| 2 | 🧾 **Explainable decision traces** | "Why did it yield?" → full reasoning chain with costs and rejected alternatives. Nobody else will have this. |
| 3 | ⚖️ **AI advises, rules decide** | Directly addresses BEL's real constraint: **black-box ML cannot pass defence safety certification.** |
| 4 | 💀 **Live SPOF demo** | Physically closing the dashboard mid-run, fleet unaffected. **10 seconds that prove the whole PS.** |
| 5 | 🔀 **Live A/B toggle** | Flip baseline ⟷ VYUHA on the same screen. The 20% isn't a claim on a slide — it's visible. |
| 6 | 📊 **Requirement traceability matrix** | Every R1–R18 mapped to a file and a test. Turns a subjective review into a checklist we've pre-passed. |
| 7 | 📡 **Realistic radio model** | Range limits, packet loss, blackout zones. Others assume perfect Wi-Fi — which is the exact thing the PS says doesn't exist. |
| 8 | 🔬 **Research-grounded choices** | Zenoh (best over Wi-Fi in published ROS 2 benchmarks), PIBT (best scaling in 2026 warehouse-MAPF benchmarks). Cite the papers in the viva. |
| 9 | 🌪️ **12 chaos scenarios** | We break our own system on stage before a judge can. |
| 10 | 🦾 **Credible hardware path** | ROS 2 bridge + Pi/Jetson budget already profiled. Not vapourware. |
| 11 | 🇮🇳 **Defence-aligned framing** | Warehouse → **ordnance depot, ammunition store, field logistics**. BEL's actual business. |

---

## 15. Hardware Deployment Path

> The PS asks for edge hardware. Even if the finale demo is simulation-first, showing a **real 2–3 robot rig** is a step-change in credibility.

### Per-Robot Bill of Materials (indicative)

| Component | Option | Purpose |
|---|---|---|
| **Compute** | Raspberry Pi 5 (8 GB) **or** Jetson Orin Nano | Runs VYUHA-Core + ROS 2 |
| **LiDAR** | RPLiDAR A1M8 / C1 | 360° obstacle sensing, localization |
| **IMU** | MPU-6050 / BNO055 | Orientation, dead-reckoning aid |
| **Drive** | 2× DC gear motors + encoders | Differential drive, odometry |
| **Motor ctrl** | ESP32 + L298N / TB6612 | Low-level velocity loop |
| **Radio** | Onboard Wi-Fi 6 (+ optional ESP-NOW) | SAMVAAD mesh |
| **Power** | 3S Li-ion + BMS + buck | Battery telemetry for the dashboard |
| **Chassis** | Aluminium/acrylic 4-wheel base | Physical footprint for collision tests |

### Compute Budget Target

| Resource | Budget per robot |
|---|---|
| CPU (planning + mesh + control) | **< 40%** of one Pi 5 core-set |
| RAM | **< 600 MB** |
| A* plan time (p95) | **< 25 ms** |
| AI inference | **< 1 ms** |
| End-to-end decision latency | **< 50 ms** |
| Mesh bandwidth | **< 30 KB/s per robot** |

---

## 👨‍💻 Team

**Jayesh Deore** — Project Lead
Third Year, Artificial Intelligence & Data Science
Ajeenkya DY Patil School of Engineering (ADYPSOE), Pune
Savitribai Phule Pune University (SPPU)

---

## 📄 License

To be finalised before public release. **Add a LICENSE file before distributing outside the team.**

---

> ### 🎯 The Pitch, In One Breath
> *"Take the server out of the warehouse. Every robot becomes its own fleet manager — planning locally, negotiating peer-to-peer, and yielding by a rule you can read in plain English. Kill the network, kill the dashboard, kill a robot: the floor keeps moving. And you can watch every decision happen, live, and ask any robot why."*
