import os
import glob
import sqlite3
import pandas as pd

def main():
    print("=== 1. PARQUET DATA LAYER ===")
    p_files = glob.glob('./parquet_data/*.parquet')
    for f in sorted(p_files):
        df = pd.read_parquet(f)
        print(f"  {os.path.basename(f)}: {len(df):,} rows")

    print("\n=== 2. PROCESSED DATA LAYER ===")
    pr_files = glob.glob('./processed_data/*.parquet')
    for f in sorted(pr_files):
        df = pd.read_parquet(f)
        print(f"  {os.path.basename(f)}: {len(df):,} rows")

    print("\n=== 3. SQLITE SERVING DATABASE LAYER ===")
    if os.path.exists("urbantransit.db"):
        conn = sqlite3.connect("urbantransit.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for t in tables:
            tname = t[0]
            cursor.execute(f"SELECT COUNT(*) FROM {tname};")
            cnt = cursor.fetchone()[0]
            print(f"  {tname}: {cnt:,} rows")
        conn.close()

if __name__ == "__main__":
    main()
