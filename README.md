# Smart Mobility Insights System 🚦

A prototype system that provides traffic and footfall insights, automated toll calculation, and safe-mobility nudges using intelligent decision logic.  
Designed for Smart City, Transportation, and Mobility hackathons.

---

## Abstract

Urban transportation systems face challenges such as congestion at entry and exit points, inefficient toll pricing, and the lack of real-time mobility guidance. This project presents a Smart Mobility Insights System that analyzes traffic patterns, automatically computes route distances, intelligently selects toll pricing models, and provides safety nudges to users.

The solution is implemented as a modular Python prototype with a CLI dashboard, focusing on backend intelligence and decision-making. While the current implementation uses simulated data, the architecture is scalable and can be directly extended to real-time sensors, cameras, GPS, RFID, or IoT systems for real-world deployment.

---

## Problem Statement

- Congestion at gates and entry points  
- Static or unfair toll pricing  
- No real-time guidance for safe travel  
- Lack of integrated mobility insights for authorities  

---

## Solution Overview

The system simulates a smart mobility engine that:
- Tracks traffic and footfall at gates
- Automatically calculates distance between routes
- Chooses the best toll pricing logic (slab or dynamic)
- Generates safe-mobility nudges based on congestion
- Provides a CLI-based dashboard for interaction

---

## Key Features

### 1. Traffic & Footfall Insights
- Counts vehicle movement at each gate
- Visualizes congestion using ASCII bar charts
- Categorizes congestion levels logically

### 2. Automated Toll Calculation
- Distance calculated automatically
- Pricing logic selected by the system itself
- Vehicle-type-based toll adjustments
- Designed for scalability to FASTag / GPS systems

### 3. Safe Mobility Nudges
- Detects congestion at entry and exit points
- Advises safer or alternate travel decisions
- Improves crowd and traffic management

### 4. Integrated CLI Dashboard
- Single menu-driven interface
- Allows users and administrators to view insights
- Demonstrates system intelligence clearly

---

## Technology Stack

| Layer | Technology | Purpose |
|------|-----------|--------|
| Programming Language | Python | Core logic and simulation |
| Interface | CLI (Terminal) | Dashboard & interaction |
| Data Handling | In-memory structures | Traffic and route simulation |
| Architecture | Modular Python | Scalability and extensibility |

---

## Project Structure

smart-mobility-insights/
├── main.py                 # CLI dashboard entry point
├── traffic_insights.py     # Traffic analysis & mobility nudges
├── distance_service.py     # Automatic distance calculation
├── toll_engine.py          # Toll computation logic
├── decision_engine.py      # Pricing model decision logic
└── README.md

---

## How to Run

python main.py

---

## Data & Simulation Note

This prototype uses simulated vehicle and route data to demonstrate system intelligence.

In real-world deployment, these inputs can be replaced by:
- CCTV / camera-based vehicle detection
- RFID / FASTag data
- GPS-based distance tracking
- IoT traffic sensors

The core decision logic remains unchanged.

---

## Hackathon Readiness

- Fully functional prototype  
- Clear real-world mapping  
- Explainable decision logic  
- Scalable architecture  
- Suitable for AMD Smart Mobility challenges  

---

## Future Enhancements

- Real-time sensor and camera integration
- AI-based traffic prediction models
- Web and mobile dashboards
- Government analytics and reporting panels

---

## Author

Developed as a Smart Mobility Hackathon Prototype  
by Saiuday Bhamidi
