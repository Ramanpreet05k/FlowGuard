# 🚦 FlowGuard

> **Stop reacting to traffic. Start predicting it.** <br>
> An enterprise-grade, predictive AI and spatial routing engine for municipal traffic management.

![Next JS](https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)

---

## 🌍 Live Deployment
* **Live Dashboard (Frontend):** https://flow-guard-five.vercel.app/
* **API Documentation (Backend):** https://flowguard-2axw.onrender.com/docs

---

## 🛑 The Problem: Analysis Paralysis
Traditional municipal traffic management relies on static heatmaps and human guesswork. Dispatchers treat a scooter parked at 2 AM the same as a heavy tanker blocking a major junction at 9 AM. This leads to wasted fleet fuel, delayed emergency responses, and cascading city-wide gridlock. 

## 🟢 The Solution: Prescriptive Intelligence
FlowGuard replaces reactive observation with an automated, end-to-end mathematical intelligence pipeline. We process raw, noisy traffic violation datasets into actionable, high-ROI dispatch routes in milliseconds.

### Core Intelligence Engines

#### 1. The Heuristic CIS Engine
We abandon standard ticket-counting. Instead, we evaluate every incident using a custom Congestion Impact Score (CIS) formula that filters out harmless infractions and flags critical bottlenecks.
$$CIS = W \times T \times L \times \Delta t$$
*(Weight × Time Multiplier × Location Criticality × Hours Blocked)*

#### 2. Autonomous Hotzone Clustering (Machine Learning)
Instead of forcing human operators to guess where traffic jams are forming, FlowGuard utilizes **DBSCAN** (Density-Based Spatial Clustering of Applications with Noise) via Scikit-Learn. The engine autonomously scans $\epsilon \approx 500m$ radii, clustering severe, high-density violations into dynamic "Hotzones" while discarding isolated low-priority anomalies as spatial noise.

#### 3. Geospatial Dispatch Routing
Standard maps use straight lines (Euclidean distance), which fails on a curved Earth. FlowGuard calculates true spherical distances using the **Haversine Formula**:
$$d = 2r \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$
This data is fed into a **Greedy Nearest-Neighbor** algorithm, dynamically calculating the absolute fastest physical route for municipal tow trucks to clear the highest-ROI clusters.

---

## 💻 Tech Stack
FlowGuard utilizes a decoupled microservice architecture to ensure zero interface lag during heavy machine learning computation.

* **Frontend (Command Center):** Next.js, React, Tailwind CSS, Leaflet (Open-source geospatial mapping).
* **Backend (Intelligence API):** Python, FastAPI, Pandas, Scikit-Learn, Numpy, Uvicorn.
* **Deployment Infrastructure:** Vercel (Edge-network frontend) & Render (Heavy-compute Python backend).

---

## 🚀 Local Development Setup

To run this project locally, you will need to start both the frontend and backend servers simultaneously.

### 1. Start the Intelligence API (Backend)
Open your terminal and navigate to the `backend` directory:
```bash
cd backend

# Install ML and API dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload
```
The API will be live at http://localhost:8000

### 2. Start the Command Center (Frontend)
Open a new terminal window and navigate to the frontend directory:

cd frontend

# Install Node dependencies
npm install

# Start the Next.js development server
npm run dev


The dashboard will be live at http://localhost:3000

# 📈 The Business Impact
Fuel & Fleet Savings: Eliminates redundant cross-city driving by generating mathematically optimal, step-by-step dispatch routes.

Economic Velocity: Heavily penalizes blockages at major commercial junctions, preventing cascading gridlock that stalls logistics chains.

Automated Decision Making: Removes human guesswork, allowing dispatchers to manage higher incident volumes strictly guided by deterministic logic.

FlowGuard doesn't just show the city where its traffic problems are; it calculates exactly how to solve them.