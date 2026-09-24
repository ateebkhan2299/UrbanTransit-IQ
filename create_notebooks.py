import nbformat as nbf
import os

os.makedirs("notebooks", exist_ok=True)

# --- Notebook 1: EDA ---
nb1 = nbf.v4.new_notebook()

nb1.cells = [
    nbf.v4.new_markdown_cell("# UrbanTransit IQ - Exploratory Data Analysis (EDA)\nThis notebook explores the transit dataset to identify patterns in passenger flow, delays, and occupancy."),
    
    nbf.v4.new_code_cell("""import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)"""),

    nbf.v4.new_markdown_cell("## 1. Load Data"),
    
    nbf.v4.new_code_cell("""# Assuming raw data is in raw_data folder
# (In the final pipeline, we read from HDFS parquet, but for EDA we can inspect raw or cleaned)
try:
    delays_df = pd.read_csv('../raw_data/delays.csv')
    trips_df = pd.read_csv('../raw_data/trips.csv')
    print("Data loaded successfully!")
    print(delays_df.head())
except FileNotFoundError:
    print("Run the data generator first to create the CSVs.")"""),

    nbf.v4.new_markdown_cell("## 2. Delay Distribution Analysis"),
    
    nbf.v4.new_code_cell("""if 'delays_df' in locals():
    plt.figure(figsize=(10, 6))
    sns.histplot(delays_df['delay_minutes'], bins=50, kde=True, color='red')
    plt.title('Distribution of Delay Minutes')
    plt.xlabel('Delay (minutes)')
    plt.ylabel('Frequency')
    plt.show()"""),

    nbf.v4.new_markdown_cell("## 3. Occupancy vs Capacity (Crowding Risk)"),
    
    nbf.v4.new_code_cell("""if 'trips_df' in locals():
    trips_df['occupancy_pct'] = (trips_df['passenger_load'] / trips_df['capacity']) * 100
    
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=trips_df['route_id'].head(1000), y=trips_df['occupancy_pct'].head(1000))
    plt.title('Occupancy Percentage by Route')
    plt.xticks(rotation=45)
    plt.show()""")
]

nbf.write(nb1, 'notebooks/01_Exploratory_Data_Analysis.ipynb')

# --- Notebook 2: ML Pipeline Comparison ---
nb2 = nbf.v4.new_notebook()

nb2.cells = [
    nbf.v4.new_markdown_cell("# UrbanTransit IQ - ML Pipeline Comparison (Phase C)\nThis notebook implements the Dual-Pipeline Comparison as per SRS requirements. We compare a standard Scikit-Learn pipeline vs a PySpark MLlib pipeline for predicting **Route Delays** and **Crowding Risk**."),
    
    nbf.v4.new_markdown_cell("## 1. Scikit-Learn Pipeline (Random Forest Regressor)"),
    
    nbf.v4.new_code_cell("""from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import time

def run_sklearn_pipeline(X, y):
    print("Starting Scikit-Learn Pipeline...")
    start_time = time.time()
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = mean_squared_error(y_test, preds, squared=False)
    
    duration = time.time() - start_time
    print(f"Sklearn Pipeline finished in {duration:.2f} seconds.")
    print(f"MAE: {mae:.2f}, RMSE: {rmse:.2f}")
    
    return {'mae': mae, 'rmse': rmse, 'time': duration}"""),
    
    nbf.v4.new_markdown_cell("## 2. PySpark MLlib Pipeline (Random Forest Regressor)"),
    
    nbf.v4.new_code_cell("""from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import RandomForestRegressor as SparkRFR
from pyspark.ml.evaluation import RegressionEvaluator

def run_pyspark_pipeline():
    print("Starting PySpark MLlib Pipeline...")
    spark = SparkSession.builder.appName("ML_Comparison").getOrCreate()
    
    # In a real run, load the parquet files here
    # data = spark.read.parquet('../hdfs_data/parquet_clean/Trips')
    
    # assemble features...
    # assembler = VectorAssembler(inputCols=["feature1", "feature2"], outputCol="features")
    # data = assembler.transform(data)
    
    # train, test = data.randomSplit([0.8, 0.2])
    # rf = SparkRFR(featuresCol="features", labelCol="delay_minutes", numTrees=50)
    # model = rf.fit(train)
    # preds = model.transform(test)
    
    # eval = RegressionEvaluator(labelCol="delay_minutes", predictionCol="prediction", metricName="rmse")
    # rmse = eval.evaluate(preds)
    
    print("PySpark Pipeline Complete (Template).")
    spark.stop()""")
]

nbf.write(nb2, 'notebooks/02_ML_Pipeline_Comparison.ipynb')

print("Jupyter notebooks created successfully!")
