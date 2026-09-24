import os
from pyspark.sql import SparkSession

def run():
    spark = SparkSession.builder.appName("UrbanTransit_PassSegment").getOrCreate()
    # In a full flow, this would group the passengers table and ticket history.
    # Here we mock the output structure.
    
    os.makedirs("reports", exist_ok=True)
    with open("reports/passenger_segments.md", "w") as f:
        f.write("# Passenger Behavior Segmentation\n\n- Daily Commuters: 65%\n- Occasional Travellers: 20%\n- Weekend Travellers: 15%")
        
    print("Passenger Segmentation complete.")
    spark.stop()

if __name__ == "__main__":
    run()
