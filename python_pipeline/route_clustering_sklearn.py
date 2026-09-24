import os
import json
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

PROCESSED_DATA_DIR = "./processed_data"
MODELS_DIR = "./models"

def train_python_route_clustering_model():
    print("=== Python DS Pipeline: Route Clustering (Scikit-Learn) ===")

    summary_path = os.path.join(PROCESSED_DATA_DIR, "summary_route_performance.parquet")
    df = pd.read_parquet(summary_path)

    feature_cols = ["avg_occupancy_pct", "total_boardings", "overcrowded_events", "avg_delay_minutes", "performance_score"]
    X = df[feature_cols]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = KMeans(n_clusters=3, random_state=42, n_init=10)
    cluster_labels = model.fit_predict(X_scaled)

    silhouette = silhouette_score(X_scaled, cluster_labels)

    print(f"\n=== PYTHON SKLEARN ROUTE CLUSTERING EVALUATION ===")
    print(f"  K-Means Cluster Count: 3")
    print(f"  Silhouette Score:     {silhouette:.4f}")

    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, "python_clustering_model.pkl")
    joblib.dump({"model": model, "scaler": scaler}, model_path)

    metrics_info = {
        "model_type": "Scikit_Learn_KMeans",
        "features": feature_cols,
        "k": 3,
        "silhouette": round(silhouette, 4),
        "cluster_centers": model.cluster_centers_.tolist()
    }

    metrics_path = os.path.join(MODELS_DIR, "python_clustering_model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics_info, f, indent=2)

    print(f"\n[SAVED] Python clustering model saved to {model_path} and {metrics_path}")
    return model, metrics_info

if __name__ == "__main__":
    train_python_route_clustering_model()
