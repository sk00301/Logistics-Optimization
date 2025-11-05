🚛 IntelliLoad: Intelligent Logistics Optimization System

An end-to-end data-driven logistics optimization and decision-support platform integrating machine learning, operations research, and interactive visualization to enhance order–vehicle assignment efficiency.

📘 Overview

IntelliLoad is designed to optimize logistics operations by intelligently assigning customer orders to an available vehicle fleet, minimizing cost and emissions while maximizing vehicle utilization.
It combines predictive modeling, optimization algorithms, and visual analytics into a single seamless workflow powered by Python and Streamlit.

🧩 Project Architecture
Stage	Description	What You’ve Achieved
0. Data Understanding & Cleaning	Load, inspect, and standardize all source CSVs	All six datasets (orders, delivery, routes, fleet, costs, warehouses) successfully loaded, normalized, validated, and summarized.
1. Data Integration Layer	Merge all relevant tables into one cohesive analytical dataset	Built unified assignment dataset (200 × 44) linking orders, vehicles, routes, and costs with derived metrics.
2. Predictive Layer (Load Utilization Model)	Predict load utilization % / overload risk	Engineered target variable load_utilization_ratio, trained regression model (MAE = 9.03, R² = 0.747), and integrated predictions into dataset.
3. Optimization Layer (Assignment Engine)	Optimize order–vehicle assignments	Solver executed successfully — 147 orders assigned with constraints on cost, emissions, and utilization. Generated optimized_assignment.csv output.
4. Streamlit Decision Dashboard	Build interactive dashboard for visualization	Streamlit app (app_intelliload.py) built for live analytics and reporting.
5. Scenario Simulation / What-If Engine	Allow users to tweak constraints & rerun optimization	To be implemented next — live parameter tuning (fuel price, CO₂ cap, utilization threshold) and re-optimization.
⚙️ Tech Stack

Languages & Tools

Python 3.11

Streamlit

Pandas, NumPy

Scikit-learn

PuLP / OR-Tools (for optimization)

Matplotlib / Plotly (visual analytics)

Environment

Tested on: Windows 10 / 11

IDE: VS Code / Jupyter Notebook

Deployment: Streamlit local app

🧠 Core Features
1. Data Integration

Combines multiple logistics datasets into one optimized analytical DataFrame (assignment_master.csv).

2. Predictive Modeling

Predicts load utilization ratio and identifies overload risks before assignment.

3. Optimization Engine

Uses linear programming to assign orders to vehicles minimizing:

Total operational cost

CO₂ emissions

Under/over-utilization penalties

4. Streamlit Dashboard

Interactive interface for:

Visualizing order–vehicle assignments

Monitoring key metrics

Loading optimized results from CSV dynamically

5. Scenario Simulation (Upcoming)

Users will be able to:

Adjust parameters like fuel price, CO₂ price, and utilization cap

Rerun optimization directly from the dashboard

📂 Repository Structure
📁 IntelliLoad/
│
├── data/
│   ├── orders.csv
│   ├── fleet.csv
│   ├── routes.csv
│   ├── delivery.csv
│   ├── warehouses.csv
│   ├── costs.csv
│   └── optimized_assignment.csv
│
├── app_intelliload.py          # Streamlit dashboard
├── optimizer.py                # Assignment optimization engine
├── README.md                   # Project documentation

| Metric                    | Description                              | Value         |
| :------------------------ | :--------------------------------------- | :------------ |
| Mean Absolute Error (MAE) | Model accuracy on utilization prediction | **9.03**      |
| R² Score                  | Model explanatory power                  | **0.747**     |
| Total Orders Optimized    | Number of assignments made               | **147 / 200** |
