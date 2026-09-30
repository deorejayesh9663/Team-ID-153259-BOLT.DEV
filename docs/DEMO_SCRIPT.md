# VYUHA Live Demo Script (7 Minutes)
**Event:** Smart India Hackathon 2026 Finals
**Audience:** Bharat Electronics Limited (BEL) Judges

### Props Required:
- 1x Laptop running NETRA dashboard (connected to projector)
- 3x Physical Raspberry Pi 5 Robots (if hardware available, else run full sim)

---

## 🕒 0:00 - 1:00 | The Hook & The Problem
**Speaker:**
"Welcome, judges. In modern smart warehouses, autonomous robots rely on a central cloud server to tell them where to go.
But what happens when the Wi-Fi drops behind a steel rack? What happens if that server crashes? The entire warehouse halts.
For defense and critical logistics, a single point of failure is unacceptable.
We built **VYUHA** — an edge-AI system that turns every robot into its own fleet manager."

*(Action: Gesture to the screen showing the NETRA Dashboard)*
"What you're looking at is NETRA, our live digital twin. There are 12 robots running right now. There is no central server coordinating them. Every robot is running an independent instance of VYUHA-Core and negotiating right-of-way over a decentralized peer-to-peer mesh."

## 🕒 1:00 - 2:30 | The Core Demo (No Server, No Collisions)
**Speaker:**
"Let's look at a critical junction."
*(Action: Click on Junction C2)*
"Notice the robots passing through. Instead of a server assigning turns, they use a deterministic Priority-Based Arbiter. Priority > Distance > ID. It is mathematically impossible for them to deadlock."

*(Action: Open the TRACES tab for AMR-03)*
"Look at this trace. AMR-03 just yielded to AMR-01. Why? Because AMR-01 is carrying an EXPRESS load. The AI advised a reroute, but the deterministic layer enforced the safety yield. Safety is hard-coded; AI is just an optimizer."

## 🕒 2:30 - 4:00 | Chaos Injections (The 'Drop the Mic' Moments)
**Speaker:**
"Now, let's break it."

**Chaos 1: The Dead Server**
*(Action: Open the Control Rail, click "Kill Dashboard Server")*
"I just killed the dashboard server. The UI is dead. Look at the floor. The robots are still moving. They don't need us. They run entirely on edge hardware."
*(Action: Restart Dashboard)*

**Chaos 2: The Blocked Aisle**
*(Action: Drop a virtual pallet into Aisle D3)*
"An aisle just got blocked. Watch AMR-04. It detects the block, stops, and gossips the hazard over the P2P mesh. Within milliseconds, the entire fleet updates their local costmaps and reroutes. No central server told them to do this."

**Chaos 3: Total Wi-Fi Blackout**
*(Action: Trigger 'C5 - Total Blackout')*
"We just killed all Wi-Fi. The mesh is down. Do they crash? No. They instantly fallback to LiDAR-only reactive safe-mode. They slow down, but they keep working."

## 🕒 4:00 - 5:30 | The AI & The Benchmark
**Speaker:**
"We were challenged to improve efficiency by 20% over standard stop-and-wait methods."
*(Action: Pull up the `throughput_vs_density.png` graph)*
"We ran 400 automated benchmark runs. Our decentralized PIBT protocol achieved a **37% reduction in makespan** with zero collisions."

*(Action: Toggle AI Advisor OFF live in the dashboard)*
"I just turned off the TinyML congestion predictor. The collisions stay at absolute zero. The fleet is just a bit slower. This proves to defense contractors that our AI is an advisory optimizer, NOT a black-box safety risk."

## 🕒 5:30 - 7:00 | Conclusion & Q&A
**Speaker:**
"VYUHA delivers:
1. Zero Single Points of Failure.
2. 37% higher efficiency.
3. 100% deterministic, explainable safety.
4. Edge-native architecture ready for Raspberry Pi 5.

Thank you. We are ready for your questions."
