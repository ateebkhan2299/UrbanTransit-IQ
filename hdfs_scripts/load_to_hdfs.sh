#!/usr/bin/env bash
# load_to_hdfs.sh - Shell script to load raw and Parquet data into HDFS

HDFS_RAW_DIR="/transport_data/raw"
HDFS_PARQUET_DIR="/transport_data/parquet"

echo "=== Loading UrbanTransit IQ Datasets into HDFS ==="

# Create HDFS destination directories
hdfs dfs -mkdir -p ${HDFS_RAW_DIR}
hdfs dfs -mkdir -p ${HDFS_PARQUET_DIR}

# Upload raw CSV and JSON files
echo "Uploading CSV and JSON files..."
hdfs dfs -put -f raw_data/*.csv ${HDFS_RAW_DIR}/
hdfs dfs -put -f raw_data/*.json ${HDFS_RAW_DIR}/

# Upload Parquet files
echo "Uploading Parquet files..."
hdfs dfs -put -f parquet_data/*.parquet ${HDFS_PARQUET_DIR}/

echo "=== Verification ==="
hdfs dfs -ls ${HDFS_RAW_DIR}
hdfs dfs -ls ${HDFS_PARQUET_DIR}

echo "[SUCCESS] Data successfully loaded into HDFS."
