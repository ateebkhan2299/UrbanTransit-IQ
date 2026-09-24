# UrbanTransit IQ — Big Data & Data Science Public Transport Analytics System

UrbanTransit IQ is a high-performance transport analytics web application powered by **two independent analytical pipelines**:
1. **Big Data Pipeline**: Apache Spark (PySpark) + Spark MLlib (Distributed GBTRegressor, RandomForest, KMeans).
2. **Python Data Science Pipeline**: Python Pandas + Scikit-Learn + XGBoost.

Both pipelines independently process public-transit telemetry (tickets, routes, trips, delays, occupancy, GPS events) and serve predictions to a **FastAPI backend** and **Vite React dashboard**.

---

## 🏗️ System Architecture & Workflow

```
[ Data Generator ] ──> Raw CSV & Parquet Telemetry
                          │
         ┌────────────────┴────────────────┐
         ▼                                 ▼
[ Big Data Pipeline ]             [ Python DS Pipeline ]
(PySpark + Spark MLlib)          (Pandas + Sklearn/XGBoost)
  • Ingestion & DQ                  • Cleaning & Imputation
  • Deduplication & Cleaning        • Feature Engineering
  • Feature Engineering             • Model Training (.pkl)
  • Spark ML Models                 • Pipeline Metrics JSON
         │                                 │
         └────────────────┬────────────────┘
                          ▼
             [ Model Comparison Engine ]
             (Spark MLlib vs. Sklearn/XGB)
                          │
                          ▼
             [ SQLite Serving Database ]
                     (urbantransit.db)
                          │
                          ▼
              [ FastAPI Backend API ]
             (http://127.0.0.1:8000)
                          │
                          ▼
            [ Vite React Frontend UI ]
             (http://127.0.0.1:5173)
```

---

## ⚡ Quick Start Guide

### 1. Requirements & Setup
- Python 3.10+
- Node.js 18+ & npm
- OpenJDK 17 LTS (configured automatically via `backend/config.py`)

```bash
# Install Python backend & pipeline dependencies
pip install -r requirements.txt

# Install React frontend dependencies
cd frontend
npm install
```

### 2. Generate Synthetic Telemetry Data
```bash
python data_generator/data_generator.py
```

### 3. Run PySpark Big Data Pipeline
```bash
python spark_jobs/01_ingest.py
python spark_jobs/02_data_quality.py
python spark_jobs/03_cleaning.py
python spark_jobs/04_joins.py
python spark_jobs/05_feature_engineering.py
python spark_jobs/06_eda.py
python spark_jobs/07_delay_prediction_mllib.py
python spark_jobs/08_demand_forecast_mllib.py
python spark_jobs/09_route_clustering_mllib.py
python spark_jobs/10_occupancy_risk_mllib.py
```

### 4. Run Python Data Science Pipeline
```bash
python python_pipeline/delay_prediction_sklearn.py
python python_pipeline/demand_forecast_sklearn.py
python python_pipeline/route_clustering_sklearn.py
python python_pipeline/occupancy_risk_sklearn.py
```

### 5. Run Dual-Pipeline Comparison & Initialize Database
```bash
python comparison/dual_pipeline_comparison.py
python backend/init_db.py
```

### 6. Start FastAPI Backend API
```bash
uvicorn backend.main:app --reload --port 8000
```
- API Documentation available at: `http://127.0.0.1:8000/docs`

### 7. Start React Frontend Dashboard
```bash
cd frontend
npm run dev
```
- Interactive Dashboard available at: `http://127.0.0.1:5173`

---

## 🧪 Automated Testing

Run full test suite across data generators, PySpark cleaning, comparison engine, and FastAPI endpoints:
```bash
pytest
```

---

## 📊 Key Features

- **Executive Overview**: Real-time KPI summaries, system on-time performance, and AI-driven operational recommendations.
- **Passenger Flow**: 24-hour network boarding volume and peak-hour distribution.
- **Route Performance Leaderboard**: Multi-criteria weighted scoring (occupancy 40% + on-time 40% + volume 20%), performance tiers (Tier A-D), and KMeans cluster labels.
- **Delay Analytics**: Root cause pie charts, delay severity histograms, and most-delayed route rankings.
- **Occupancy Risk**: Overcrowding hotspot detection and hourly capacity utilization curves.
- **Predictive Demand Forecasting**: 7-day passenger demand forecasts with 95% confidence intervals.
- **Interactive Route Map**: Leaflet geospatial route alignment and stop delay markers.
- **What-If Simulator**: Real-time fleet, headway, and vehicle capacity simulation.
- **Dual-Pipeline Comparison Matrix**: Side-by-side benchmarking of Big Data (Spark MLlib) vs Python (Scikit-Learn/XGBoost) model metrics (RMSE, MAE, R², F1, Accuracy, Precision, Recall).
