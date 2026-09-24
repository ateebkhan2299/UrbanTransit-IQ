# AI Usage & Prompt Engineering Log — UrbanTransit IQ

## 1. Overview
This project was developed in pair-programming collaboration with **Antigravity (Google DeepMind)** adhering strictly to the single source of truth master build plan.

## 2. Phases Executed & AI Tool Interaction

| Phase | Description | AI Assistance & Artifacts | Status |
|---|---|---|---|
| **Phase 1** | Data Generator (12 domain tables, anomalies) | Data generation script & synthetic anomaly injection validation (`test_data_generator.py`). | Completed |
| **Phase 2** | HDFS & Ingestion Pipeline | HDFS script, explicit PySpark schemas, Windows `winutils.exe` native wrapper. | Completed |
| **Phase 3** | Data Quality & Cleaning Pipeline | Data quality report export, PySpark null imputation & deduplication (`test_data_quality.py`). | Completed |
| **Phase 4** | Relational Joins & Feature Engineering | Multi-table PySpark joins, domain metrics (`occupancy_pct`, `is_overcrowded`, `headway_minutes`). | Completed |
| **Phase 5** | EDA & Route Scoring Engine | Weighted multi-criteria route scoring `(occupancy*0.4 + on_time*0.4 + volume*0.2)`. | Completed |
| **Phase 6** | PySpark MLlib Predictive Models | GBTRegressor, RandomForestRegressor, KMeans (k=3), RandomForestClassifier training & metric export. | Completed |
| **Phase 7** | Python Data Science Pipeline | Independent Pandas / Scikit-Learn / XGBoost data cleaning, feature engineering, and model training. | Completed |
| **Phase 8** | Dual-Pipeline Comparison Engine | Benchmarking Spark MLlib vs Python Scikit-Learn models on held-out test cases (`test_spark_vs_python.py`). | Completed |
| **Phase 9** | Database & Serving Layer | SQLAlchemy ORM models, SQLite initialization & Parquet data loading (`urbantransit.db`). | Completed |
| **Phase 10** | FastAPI Backend API Routers | Pydantic schemas & 8 REST routers (`dashboard`, `routes`, `delays`, `occupancy`, `forecast`, `recommendations`, `whatif`, `comparison`). | Completed |
| **Phase 11** | React Frontend Dashboard | Vite React SPA with Tailwind CSS, Recharts, Leaflet route maps, What-If sliders, and comparison tables. | Completed |
| **Phase 12** | Verification & Final Test Suite | Full pytest suite run across all modules (18/18 tests passed, 100% pass rate). | Completed |

## 3. Engineering Decisions & Technical Solutions
- **Dynamic Java Runtime Resolution**: Automatically selects OpenJDK 17 LTS (`C:\Program Files\Tableau\Tableau 2026.2\bin\jre`) to ensure PySpark compatibility on Windows without user intervention.
- **Parquet Integer Compatibility**: Used `LongType()` in PySpark schema definition to maintain binary schema equivalence with 64-bit integer Parquet files produced by PyArrow.
- **Hadoop Permission Bypass**: Automated PowerShell C# compilation of a native `winutils.exe` stub to bypass Windows POSIX permission exceptions in local PySpark context.
