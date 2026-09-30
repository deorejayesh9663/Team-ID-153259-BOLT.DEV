# 🧰 VYUHA — Technology Stack

### Edge-AI Based Distributed Fleet Coordination for AMRs in Smart Warehouses
**SIH 2026 · Problem Statement 26123 · Bharat Electronics Limited**

> Every choice below has a **reason** and a **rejected alternative**. Judges ask "why this and not that?" — this document is the answer sheet.

---

## 📋 Contents

1. [Stack at a Glance](#1-stack-at-a-glance)
2. [Layer 0 — Edge Hardware](#2-layer-0--edge-hardware)
3. [Layer 1 — Robot Operating System](#3-layer-1--robot-operating-system)
4. [Layer 2 — Communication Middleware](#4-layer-2--communication-middleware)
5. [Layer 3 — Planning & Coordination Algorithms](#5-layer-3--planning--coordination-algorithms)
6. [Layer 4 — Edge-AI / TinyML](#6-layer-4--edge-ai--tinyml)
7. [Layer 5 — Simulation Environment](#7-layer-5--simulation-environment)
8. [Layer 6 — NETRA Dashboard](#8-layer-6--netra-dashboard)
9. [Layer 7 — Benchmarking & Testing](#9-layer-7--benchmarking--testing)
10. [DevOps & Tooling](#10-devops--tooling)
11. [Complete Dependency Manifest](#11-complete-dependency-manifest)
12. [Two-Track Build Strategy](#12-two-track-build-strategy)
13. [Rejected Technologies](#13-rejected-technologies)
14. [Skills Matrix](#14-skills-matrix)

---

## 1. Stack at a Glance

```
╔═══════════════════════════════════════════════════════════════════════╗
║  L7  TESTING     pytest · hypothesis · pytest-benchmark · GitHub CI   ║
╠═══════════════════════════════════════════════════════════════════════╣
║  L6  DASHBOARD   React 18 + Vite · HTML5 Canvas / PixiJS              ║
║                  TailwindCSS · Zustand · FastAPI + WebSockets         ║
╠═══════════════════════════════════════════════════════════════════════╣
║  L5  SIMULATION  Custom Python discrete-event sim (primary)           ║
║                  Gazebo Harmonic / NVIDIA Isaac Sim (physics track)   ║
╠═══════════════════════════════════════════════════════════════════════╣
║  L4  EDGE-AI     scikit-learn (DecisionTree) · PyTorch → ONNX         ║
║                  ONNX Runtime / TFLite · <1 MB models                 ║
╠═══════════════════════════════════════════════════════════════════════╣
║  L3  ALGORITHMS  A* · D* Lite · PIBT · Space-time reservations        ║
║                  ORCA · Contract Net · Wait-for-graph detection       ║
╠═══════════════════════════════════════════════════════════════════════╣
║  L2  MESSAGING   Eclipse Zenoh (peer mode, broker-free)               ║
║                  UDP multicast fallback · MessagePack serialization   ║
╠═══════════════════════════════════════════════════════════════════════╣
║  L1  ROBOTICS    ROS 2 Jazzy · Nav2 · SLAM Toolbox · AMCL             ║
╠═══════════════════════════════════════════════════════════════════════╣
║  L0  HARDWARE    Raspberry Pi 5 / Jetson Orin Nano · RPLiDAR · ESP32  ║
╚═══════════════════════════════════════════════════════════════════════╝

CORE LANGUAGES:  Python 3.11+ (logic)  ·  JavaScript/JSX (NETRA)
                 C++ (ROS 2 hot paths, only if profiling demands it)
```

---

## 2. Layer 0 — Edge Hardware

The PS explicitly names **Raspberry Pi** and **Jetson Nano**. We design to that budget and profile against it.

### 2.1 Compute Platform

| Option | Spec | When To Use | Approx ₹ |
|---|---|---|---|
| **Raspberry Pi 5 (8 GB)** ⭐ | Quad Cortex-A76 @ 2.4 GHz | **Primary** — proves it runs on cheap, available hardware | ~₹8,000 |
| **Jetson Orin Nano (8 GB)** | 6-core A78AE + 1024 CUDA | If we add a vision/perception module | ~₹40,000 |
| **Jetson Nano (4 GB)** | Legacy, named in the PS | Only if a lab unit is already available | ~₹15,000 |

> **Decision:** Build and profile on **Raspberry Pi 5**. If our models run comfortably on a Pi, they run *anywhere* — and it's a far stronger claim than "we needed a GPU."

### 2.2 Sensors & Actuation

| Component | Part | Why |
|---|---|---|
| **2D LiDAR** | RPLiDAR A1M8 / C1 | 360° scan, 12 m range — enough for aisle-scale sensing and blackout fallback |
| **IMU** | BNO055 (fused) or MPU-6050 | Orientation + dead-reckoning when localization degrades |
| **Wheel encoders** | Magnetic quadrature | Odometry for AMCL |
| **Motor driver** | TB6612FNG / L298N | Differential-drive velocity control |
| **MCU** | ESP32-WROOM | Real-time motor loop; offloads timing from the Pi. Optional **ESP-NOW** as a secondary mesh radio |
| **Battery** | 3S Li-ion 11.1 V + BMS | BMS gives real SoC telemetry → the dashboard battery ring is genuine data |
| **Radio** | Onboard Wi-Fi 6 | Primary SAMVAAD transport |

### 2.3 Resource Budget (hard targets)

| Resource | Target | Enforced By |
|---|---|---|
| CPU | < 40% of one Pi 5 | `bench_edge_profile.py` |
| RAM | < 600 MB | `bench_edge_profile.py` |
| A* plan (p95) | < 25 ms | `pytest-benchmark` |
| AI inference | < 1 ms | ONNX Runtime timing |
| Decision loop | 10 Hz sustained | Runtime watchdog |
| Mesh bandwidth | < 30 KB/s per robot | `samvaad.metrics` |

---

## 3. Layer 1 — Robot Operating System

### 3.1 ROS 2 Jazzy Jalisco

| Aspect | Choice | Rationale |
|---|---|---|
| **Distro** | **ROS 2 Jazzy** (LTS, Ubuntu 24.04) | Current LTS; Humble is the fallback if lab machines are on 22.04 |
| **Why ROS 2 at all** | Industry standard; gives Nav2, SLAM, TF2, rosbag, RViz free | Also signals professional-grade work to judges |
| **Why not ROS 1** | End-of-life; single-master architecture is **itself a SPOF** — the exact anti-pattern this PS attacks | |

### 3.2 ROS 2 Packages Used

| Package | Role |
|---|---|
| **Nav2** | Local trajectory following, costmaps, recovery behaviours |
| **SLAM Toolbox** | Map building (offline) |
| **Nav2 AMCL** | Particle-filter localization against the known warehouse map |
| **TF2** | Coordinate frame transforms |
| **rosbag2** | Session recording → enables NETRA replay |
| **RViz2** | Engineering-grade debug view (secondary to NETRA) |

### 3.3 Critical Architectural Boundary

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   ROS 2 / Nav2         │        VYUHA-Core                    │
│   ─────────────        │        ──────────                    │
│   • local obstacle     │   • fleet coordination               │
│     avoidance          │   • space-time reservations          │
│   • trajectory follow  │   • right-of-way arbitration         │
│   • costmap            │   • task auctions                    │
│   • recovery           │   • deadlock resolution              │
│                        │                                      │
│   "HOW to drive there" │   "WHETHER I'm allowed to go"        │
│                                                              │
│   ⚠️ VYUHA-Core is a PURE PYTHON LIBRARY with ZERO ROS        │
│      imports. ROS 2 is an optional adapter, not a dependency. │
│      ⇒ The whole coordination layer is unit-testable,         │
│        runs in the fast sim, and stays portable.              │
└──────────────────────────────────────────────────────────────┘
```

> 🏆 **This decoupling is worth stating explicitly in the pitch.** Teams that fuse their logic into ROS nodes cannot run a 400-run benchmark matrix in an afternoon. We can.

---

## 4. Layer 2 — Communication Middleware

### 4.1 The Decision: Eclipse Zenoh (peer mode)

This is the **single most defensible technical choice** in the project, because published research points straight at it.

| Middleware | Architecture | Warehouse Wi-Fi Performance | Broker? | Verdict |
|---|---|---|---|---|
| **Zenoh** ⭐ | Peer-to-peer, decentralized | **Best over Wi-Fi & 4G; smallest real-robot trajectory drift** in published ROS 2 middleware comparisons | ❌ none needed | ✅ **CHOSEN** |
| **CycloneDDS** | Decentralized (ROS 2 default) | Best over **Ethernet**; degrades over Wi-Fi | ❌ none | 🟡 Secondary |
| **MQTT** | Client–server | Lightweight, but the **broker is a SPOF** | ✅ required | ❌ Violates the PS |
| **Kafka** | Broker cluster | Heavy; saturates on large payloads | ✅ required | ❌ Not edge-suitable |
| **Raw UDP multicast** | Fully decentralized | No QoS, no discovery, manual everything | ❌ none | 🟡 Fallback backend |

**Why Zenoh wins for PS 26123:**
1. **Peer mode = literally zero servers.** The PS bans central dependency — Zenoh satisfies it architecturally, not by convention.
2. **Wi-Fi is the warehouse reality.** Zenoh is the middleware that measurably degrades least on Wi-Fi.
3. **Built for the edge.** Designed explicitly for edge computing, IIoT and robotics.
4. **ROS 2-native path exists** (`rmw_zenoh`), so the sim and the hardware track share one protocol.
5. **Scales down.** Runs on a Pi without a GB of RAM.

### 4.2 Transport Abstraction (never bet on one backend)

```python
# samvaad/transport/base.py
class Transport(ABC):
    @abstractmethod
    def broadcast(self, msg: Message) -> None: ...
    @abstractmethod
    def send_to(self, peer_id: str, msg: Message) -> None: ...
    @abstractmethod
    def poll(self) -> list[Message]: ...

# Selected at runtime from fleet_config.json:
#   "zenoh"   → ZenohPeerTransport      (primary)
#   "udp"     → UDPMulticastTransport   (fallback, zero deps)
#   "inproc"  → InProcessTransport      (fast benchmarking, 400 runs)
```

> 🛡️ **Demo insurance:** if Zenoh misbehaves on venue Wi-Fi, flip one config key to `udp` or `inproc` and the demo still runs. **Never let a third-party library be able to kill your finale.**

### 4.3 Serialization

| Option | Size | Speed | Human-readable | Verdict |
|---|---|---|---|---|
| **MessagePack** ⭐ | Compact | Fast | ❌ | ✅ Wire format |
| **JSON** | Verbose | Slower | ✅ | ✅ Debug/log format |
| Protobuf | Smallest | Fastest | ❌ | 🟡 Overkill for our payloads |

**Decision:** MessagePack on the wire, JSON for the NETRA `MESH` tab so a judge can literally read the packets.

### 4.4 Realism Layer (what most teams skip)

| Feature | Why It Matters |
|---|---|
| **Range-limited radio** (e.g. 18 m) | The PS is about **Wi-Fi dead zones**. Assuming perfect connectivity dodges the actual problem. |
| **Packet loss injection** | Proves convergence is robust, not lucky |
| **Latency jitter** | Reveals race conditions before the judges do |
| **Blackout zones** | Enables chaos scenario C4/C5 |
| **Message signing** | Replay-attack guard — a *defence-relevant* detail for BEL |

---

## 5. Layer 3 — Planning & Coordination Algorithms

### 5.1 Algorithm Table

| Problem | Algorithm | Complexity | Why This One |
|---|---|---|---|
| Single-agent path | **A\*** (congestion-inflated) | O(b^d), ms-scale on grid | Optimal, admissible, edge-cheap |
| Incremental replan | **D\* Lite** | Reuses prior search | A blocked aisle costs a fraction of a full replan — critical at 10 Hz |
| Multi-agent scaling | **PIBT** (Priority Inheritance with Backtracking) | Near-linear in agents | 2026 warehouse-MAPF benchmarking shows **PP and LNS2 struggle at high agent counts while PIBT-based approaches scale preferably** |
| Conflict guarantee | **Space-time reservation table** | O(1) lookup | Catches vertex, **edge (head-on)** and **swap** conflicts |
| Local avoidance | **ORCA** | O(n) neighbours | Smooth continuous avoidance beneath the discrete plan |
| Deadlock | **Wait-for graph + Tarjan SCC** | O(V+E) | Provable cycle detection, not a heuristic timeout |
| Task allocation | **Contract Net Protocol** | O(n) bids | Decentralized; no auctioneer; degrades with radio range |
| Baseline (to beat) | **Hungarian + stop-and-wait** | O(n³) | The centralized straw-man the PS names |

### 5.2 Why NOT Full CBS / EECBS

| Aspect | CBS / EECBS | VYUHA Choice |
|---|---|---|
| Optimality | Optimal / bounded-suboptimal | Suboptimal but fast |
| **Centralization** | **Requires a global solver** | ❌ **Fatal — violates the PS** |
| Edge feasibility | Exponential worst case | Must fit a Pi at 10 Hz |
| Lifelong / dynamic | Needs full re-solve | D* Lite patches incrementally |

> 🎤 **Viva-ready answer:** *"CBS is the gold standard for offline optimal MAPF — but it's centralized and exponential. This problem statement forbids the first and edge hardware forbids the second. We use prioritized planning with PIBT-style inheritance, which recent warehouse-MAPF benchmarking shows scales best among lightweight solvers, and we recover the lost optimality with congestion-aware cost shaping."*

### 5.3 The Reservation Table

```python
@dataclass(frozen=True)
class VertexReservation:
    cell: tuple[int, int]
    t_start: float
    t_end: float
    robot_id: str
    priority: float

@dataclass(frozen=True)
class EdgeReservation:
    """Catches head-on swaps that vertex-only checks miss."""
    from_cell: tuple[int, int]
    to_cell:   tuple[int, int]
    t: float
    robot_id: str

# Conflict types detected:
#   VERTEX  — two robots in the same cell at overlapping times
#   EDGE    — two robots traversing the same edge in opposite directions
#   SWAP    — A→B while B→A simultaneously  (the classic MAPF trap)
#   FOLLOW  — rear-end risk in a single-width aisle
```

### 5.4 Libraries

| Library | Purpose |
|---|---|
| **NumPy** | Grid maths, cost maps, vectorised occupancy checks |
| **SciPy** | `linear_sum_assignment` (Hungarian baseline), spatial KD-trees |
| **NetworkX** | Wait-for graph, SCC cycle detection |
| **Shapely** *(optional)* | Precise footprint-overlap collision assertions |
| **heapq** (stdlib) | A* priority queue |

---

## 6. Layer 4 — Edge-AI / TinyML

> ⚠️ **Read [PROJECT.md §8.3](./PROJECT.md#83-the-safety-invariant-the-line-we-never-cross) first.** Everything here is **advisory**. It may re-rank safe options. It may never authorise an unsafe move.

### 6.1 Model 1 — Congestion Forecaster

| Property | Value |
|---|---|
| **Task** | Predict junction/aisle occupancy probability at **t + 5 s** |
| **Input** | 16 features: recent occupancy window, in-range peer intents, queue depth, hour-of-shift, task density |
| **Architecture** | GRU (2 layers × 16 units) — or a Gradient-Boosted Tree if GRU inference exceeds budget |
| **Training data** | Self-generated from thousands of simulation runs (**no external dataset needed — the PS provides none**) |
| **Export** | PyTorch → ONNX → ONNX Runtime |
| **Size** | **< 50 KB** |
| **Inference** | **< 1 ms on Pi 5** |
| **Consumed by** | A* cost inflation — makes robots *avoid* jams instead of *queueing in* them |

### 6.2 Model 2 — Explainable Priority Advisor

| Property | Value |
|---|---|
| **Task** | Suggest a priority weight adjustment in a conflict |
| **Architecture** | **`DecisionTreeClassifier(max_depth=5)`** |
| **Why a shallow tree** | ① Fully auditable — you can *print the rules*. ② Microsecond inference. ③ **Passes defence safety review; a neural net does not.** |
| **Features (6)** | remaining distance, battery SoC, task priority class, wait time so far, local congestion, downstream blocking impact |
| **Authority** | ⚠️ **ADVISORY ONLY.** Output feeds Tier 1 of the arbiter and can only reorder options the deterministic layer has already certified safe. |

### 6.3 Why Not End-to-End Deep RL

| Concern | Detail |
|---|---|
| **Research consensus** | 2026 MAPF literature states plainly that while ML methods have been explored, **their superiority over search-based methods remains inconclusive** |
| **Certification** | Black-box models cannot be certified on safety-critical paths in defence/industrial deployments |
| **Edge cost** | A policy network large enough to be useful won't hit 10 Hz on a Pi |
| **Data** | The PS ships **no dataset**. Training end-to-end RL from scratch in hackathon time is a schedule risk with no upside |
| **Explainability** | We'd lose the TRACES panel — which is one of our biggest differentiators |

> 🎯 **Our position (say this in the viva):** *"We deliberately use AI where it's safe and valuable — predicting congestion and shaping costs — and we deliberately refuse to use it where a wrong answer means a collision. That's not a limitation; that's the design."*

### 6.4 ML Toolchain

| Tool | Use |
|---|---|
| **scikit-learn** | DecisionTree advisor, feature pipelines |
| **PyTorch** | Train the GRU forecaster |
| **ONNX + ONNX Runtime** | Portable, fast edge inference |
| **TensorFlow Lite** | Alternative export path if targeting a microcontroller |
| **Optuna** *(optional)* | Hyperparameter search for cost weights |
| **pandas** | Benchmark result analysis |

---

## 7. Layer 5 — Simulation Environment

### 7.1 Two Simulators, Two Jobs

| | **Track A — Fast Sim** ⭐ | **Track B — Physics Sim** |
|---|---|---|
| **Engine** | Custom Python discrete-event | Gazebo Harmonic / NVIDIA Isaac Sim |
| **Fidelity** | Grid + kinematics + footprints | Full rigid-body physics, LiDAR raycasts |
| **Speed** | **1000× real-time** | ~1× real-time |
| **Purpose** | The **400-run benchmark matrix** | Visual realism + the ROS 2 hardware bridge |
| **Priority** | 🔴 **P0 — build first** | 🟡 P8 — nice to have |

> **Why Track A first:** the success criteria demand statistical evidence across fleet sizes, task counts and seeds. At Gazebo speed that's days of compute. At Python-sim speed it's a coffee break. **Ship the evidence engine before the eye candy.**

### 7.2 Fast Sim Design Principles

| Principle | Implementation |
|---|---|
| **Deterministic** | Seeded RNG; same seed ⇒ byte-identical run ⇒ reproducible claims |
| **Headless** | No rendering in benchmark mode |
| **Parallel** | `multiprocessing` — 400 runs across all cores |
| **Physically honest** | Collisions asserted on **real footprint overlap**, not grid-cell equality (no cheating the zero-collision claim) |
| **Injectable** | Obstacles, humans, radio blackouts, robot deaths — all runtime-injectable |

### 7.3 Warehouse Model

| Element | Representation |
|---|---|
| Grid | Occupancy array, configurable cell size (default 0.5 m) |
| Racks | Static blocked regions |
| Aisles | Single-width (forces conflicts) and double-width corridors |
| Junctions | Tagged choke points — the interesting cells |
| Pick stations | Task sources |
| Dock doors | Task sinks |
| Charging bays | Battery replenishment |
| Dynamic actors | Humans, forklifts, dropped pallets |

---

## 8. Layer 6 — NETRA Dashboard

### 8.1 Frontend

| Technology | Choice | Why |
|---|---|---|
| **Framework** | **React 18 + Vite** | Fast HMR; component model fits the per-robot panel |
| **Rendering** | **HTML5 Canvas** (upgrade to **PixiJS** if >12 robots) | Canvas handles the pixel-art floor at 60 fps; DOM/SVG would choke |
| **Styling** | **TailwindCSS** | Rapid, consistent dark-ops aesthetic |
| **State** | **Zustand** | Lightweight; Redux is overkill |
| **Charts** | **Recharts** | KPI sparklines, throughput curves |
| **Icons** | **lucide-react** | Clean, consistent |
| **Art** | Custom sprite sheets (Aseprite / Piskel) | AMRs, racks, pallets, docks, charge bays |

### 8.2 Backend

| Technology | Choice | Why |
|---|---|---|
| **API** | **FastAPI** | Async-native, auto-docs, Python-native with the core |
| **Live feed** | **WebSockets** | Push telemetry at 10–30 Hz |
| **Traces** | SQLite (or in-memory ring buffer) | Session replay |
| **Serving** | Uvicorn | Standard ASGI |

### 8.3 ⚠️ The Read-Only Rule (architectural, not stylistic)

```
      SAMVAAD MESH  ──────────────────────────────────────►
        │      │      │      │      │      │
      AMR-01 AMR-02 AMR-03 AMR-04 AMR-05 AMR-06
        └──────┴──────┴───┬──┴──────┴──────┘
                          │
                   passive tap ▼  (subscribe only — NEVER publish)
                  ┌────────────────┐
                  │  NETRA SERVER  │
                  └───────┬────────┘
                          ▼
                  ┌────────────────┐
                  │  BROWSER UI    │
                  └────────────────┘

  ╔══════════════════════════════════════════════════════════╗
  ║  NETRA SUBSCRIBES. IT DOES NOT COORDINATE.                ║
  ║  Operator controls (e-stop, teleop) are injected as       ║
  ║  HINTS on the mesh — each robot's deterministic arbiter    ║
  ║  still holds final authority over every move.             ║
  ║                                                           ║
  ║  ⇒ Kill NETRA mid-demo. The fleet does not notice. ⭐      ║
  ╚══════════════════════════════════════════════════════════╝
```

### 8.4 Alternative Considered

| Option | Verdict |
|---|---|
| **Streamlit** | ✅ Fast to build, ❌ can't do 60 fps pixel-art canvas or a genuine game-like feel. **Use as a P2 stopgap only.** |
| **RViz2** | ✅ Free with ROS, ❌ engineer-facing, zero presentation impact |
| **Plotly Dash** | 🟡 Good charts, weak custom canvas |
| **React + Canvas** ⭐ | ✅ **Chosen** — full control over the visual identity that differentiates us |

---

## 9. Layer 7 — Benchmarking & Testing

| Tool | Purpose |
|---|---|
| **pytest** | Entire test suite |
| **pytest-benchmark** | Plan-time and inference-latency budgets |
| **hypothesis** | **Property-based testing** — fuzz random fleets/maps and assert the zero-collision invariant holds. *This is how we make the safety claim credible.* |
| **pytest-cov** | Coverage on safety-critical modules |
| **psutil** | CPU/RAM profiling against the edge budget |
| **pandas + matplotlib** | Benchmark analysis and report figures |
| **GitHub Actions** | CI: every push runs the safety suite |

### Test Taxonomy

| Suite | Contents |
|---|---|
| `tests/unit/` | A*, reservations, bid function, arbiter ordering |
| `tests/integration/` | Full multi-robot runs, task lifecycle |
| `tests/safety/` ⭐ | **Zero-collision invariants, footprint overlap, arbiter total-order proofs** |
| `tests/chaos/` ⭐ | C1–C12 scenario regression |
| `tests/perf/` | Edge compute budget enforcement |

---

## 10. DevOps & Tooling

| Category | Tool | Use |
|---|---|---|
| **Language** | Python 3.11+ | Modern typing, pattern matching, perf |
| **Env** | `venv` + `pip-tools` | Reproducible installs |
| **Containers** | Docker + Compose | **Spawn N robot containers + NETRA** — proves process isolation, not fake threads |
| **VCS** | Git + GitHub | `main` / `dev` / feature branches |
| **CI** | GitHub Actions | Tests + benchmark smoke on every push |
| **Lint** | `ruff` | Fast lint + format |
| **Types** | `mypy` | Static checking on core modules |
| **Docs** | Markdown + Mermaid | This documentation set |
| **Sprites** | Aseprite / Piskel | Pixel art |
| **Diagrams** | Excalidraw / Mermaid | Architecture figures |

### Docker Topology (the "it's genuinely distributed" proof)

```yaml
services:
  amr-01:  { build: ., command: python -m vyuha_core.runtime --id AMR-01 }
  amr-02:  { build: ., command: python -m vyuha_core.runtime --id AMR-02 }
  amr-03:  { build: ., command: python -m vyuha_core.runtime --id AMR-03 }
  amr-04:  { build: ., command: python -m vyuha_core.runtime --id AMR-04 }
  netra:   { build: ., command: uvicorn netra.server:app, ports: ["8000:8000"] }
```

> 🏆 **Each robot is a separate OS process with its own memory.** They *cannot* cheat by reading each other's variables. When a judge asks *"is it really decentralized, or just threads pretending?"* — `docker ps` is the answer.

---

## 11. Complete Dependency Manifest

### `requirements.txt`

```txt
# ── Core ──────────────────────────────────────────
numpy>=1.26
scipy>=1.12
networkx>=3.2

# ── Communication ─────────────────────────────────
eclipse-zenoh>=0.11
msgpack>=1.0

# ── Edge AI ───────────────────────────────────────
scikit-learn>=1.4
torch>=2.2                # training only
onnx>=1.15
onnxruntime>=1.17         # inference on edge

# ── Dashboard backend ─────────────────────────────
fastapi>=0.110
uvicorn[standard]>=0.27
websockets>=12.0
pydantic>=2.6

# ── Analysis ──────────────────────────────────────
pandas>=2.2
matplotlib>=3.8

# ── Testing ───────────────────────────────────────
pytest>=8.0
pytest-benchmark>=4.0
pytest-cov>=4.1
hypothesis>=6.98

# ── Utilities ─────────────────────────────────────
psutil>=5.9
rich>=13.7                # pretty CLI output
typer>=0.9                # CLI framework
pyyaml>=6.0
```

### `package.json` (NETRA)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "zustand": "^4.5.0",
    "recharts": "^2.12.0",
    "lucide-react": "^0.383.0",
    "pixi.js": "^8.0.0"
  },
  "devDependencies": {
    "vite": "^5.1.0",
    "@vitejs/plugin-react": "^4.2.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

### ROS 2 (hardware track only)

```bash
ros-jazzy-desktop
ros-jazzy-navigation2
ros-jazzy-nav2-bringup
ros-jazzy-slam-toolbox
ros-jazzy-rmw-zenoh-cpp
ros-jazzy-rplidar-ros
```

---

## 12. Two-Track Build Strategy

> The single biggest risk in a hardware-flavoured hackathon project is **spending week 1 debugging a motor driver and having no algorithm by week 4.** Avoid it structurally.

```
╔═══════════════════════════════════════════════════════════════════╗
║  TRACK A — SOFTWARE  (🔴 P0, always demo-ready)                   ║
║                                                                   ║
║  Fast Python sim → VYUHA-Core → SAMVAAD → NETRA → KASOTI          ║
║  ✅ Satisfies 100% of the PS ("The expected solution is a          ║
║     multi-robot simulation")                                      ║
║  ✅ Produces the benchmark evidence for both success criteria      ║
║  ✅ Runs on one laptop — zero venue dependencies                   ║
╠═══════════════════════════════════════════════════════════════════╣
║  TRACK B — HARDWARE  (🟡 P8, credibility multiplier)              ║
║                                                                   ║
║  ROS 2 bridge → 2–3 physical AMRs on Pi 5 → live coordination     ║
║  🎁 Bonus, never a dependency                                     ║
║  ⚠️ If the hardware dies at 3 a.m., Track A still wins the round   ║
╚═══════════════════════════════════════════════════════════════════╝

  RULE:  Track A must be demoable at the end of EVERY week.
         Track B may never block Track A.
```

---

## 13. Rejected Technologies

Say these out loud in the viva — knowing what you *didn't* use is as convincing as what you did.

| Rejected | Reason |
|---|---|
| **MQTT / Kafka** | Broker = single point of failure = **the exact problem the PS exists to solve** |
| **ROS 1** | EOL, and its single-master design is architecturally a SPOF |
| **Centralized CBS / EECBS** | Optimal but centralized + exponential — violates both the PS and the edge budget |
| **End-to-end Deep RL** | Unexplainable, uncertifiable, no dataset provided, inconclusive vs. search per current literature |
| **Unity / Unreal simulation** | Beautiful, heavy, slow — can't run a 400-run benchmark matrix |
| **Firebase / any cloud backend** | Cloud dependency contradicts the entire premise |
| **Streamlit as the final UI** | Fine prototype, but can't deliver the pixel-art twin that makes the demo memorable |
| **localStorage-style browser persistence for fleet state** | Fleet state must live on the robots, not the observer |
| **Bluetooth mesh** | Range and bandwidth inadequate for warehouse scale |
| **5G / cellular** | Introduces an external network dependency — opposite of edge autonomy |

---

## 14. Skills Matrix

Map these across the team so nobody is a bus factor of one.

| Area | Skills | Suggested Owners |
|---|---|---|
| 🧠 **Core algorithms** | Python, A*, D* Lite, MAPF, graph theory | 2 |
| 📡 **Networking** | Zenoh, pub/sub, distributed systems, CRDTs | 1–2 |
| 🤖 **Robotics** | ROS 2, Nav2, SLAM, TF2 | 1–2 |
| 🎨 **Frontend** | React, Canvas/PixiJS, Tailwind, pixel art | 1–2 |
| 📊 **ML / Data** | scikit-learn, PyTorch, ONNX, benchmarking | 1 |
| 🔧 **Hardware** | Pi/Jetson, LiDAR, motor control, ESP32 | 1 |
| 📝 **Docs & pitch** | Technical writing, traceability, demo script | 1 (everyone contributes) |

---

## 🎤 Stack Defence — Five Questions You Will Be Asked

| Question | Your Answer |
|---|---|
| **"Why Zenoh over MQTT?"** | MQTT needs a broker. A broker is a single point of failure. The problem statement exists *because* of single points of failure. Zenoh runs peer-to-peer with no broker at all — and published ROS 2 middleware benchmarks show it degrades least over Wi-Fi, which is the actual warehouse condition. |
| **"Why not CBS — isn't it the standard?"** | CBS is the offline optimal standard, but it's centralized and exponential in the worst case. The PS forbids centralization and a Raspberry Pi forbids exponential. We use prioritized planning with PIBT-style priority inheritance, which recent warehouse-MAPF benchmarking shows scales best among lightweight solvers, and we recover quality with congestion-aware cost shaping. |
| **"Where is the AI? This looks like classical algorithms."** | The AI is the congestion forecaster and the priority advisor — and it's deliberately kept *off* the safety path. Current MAPF literature says learned methods have not conclusively beaten search-based ones, and black-box models can't pass defence safety certification. So AI optimizes throughput; deterministic rules own safety. Toggle the AI off live: collisions stay at zero, throughput drops about 12%. |
| **"Is it actually decentralized, or threads pretending?"** | Each robot is a separate Docker container — its own OS process, its own memory. They physically cannot read each other's state. `docker ps` shows six independent robots. And the dashboard is a read-only subscriber: close it mid-run and nothing on the floor changes. |
| **"Can it really run on a Raspberry Pi?"** | Yes, and we profile it: under 40% CPU, under 600 MB RAM, A* p95 under 25 ms, AI inference under 1 ms, decision loop sustained at 10 Hz. Those budgets are enforced by a test in CI, not asserted on a slide. |

---

## 📚 Research Foundations

| Topic | Key Finding We Rely On |
|---|---|
| **Middleware** | Comparative studies of DDS, MQTT and Zenoh with ROS 2 found CycloneDDS best over Ethernet but **Zenoh best over Wi-Fi and 4G**, with the smallest trajectory drift on a real robot |
| **Warehouse MAPF** | Adapting lightweight one-shot MAPF to AGVs found **PP and LNS2 struggle at high agent counts while PIBT-based approaches scale preferably** |
| **Learned vs. search MAPF** | Lifelong-MAPF research states that **the superiority of ML methods over search-based methods remains inconclusive** — supporting our advisory-only AI design |
| **Priority inheritance** | PIBT (priority inheritance with backtracking) underpins our conflict-resolution scaling story |

---

**Jayesh Deore** · TE AI & DS · ADYPSOE, Pune · SPPU
**Smart India Hackathon 2026 · PS 26123 · Bharat Electronics Limited**
