import time
import subprocess
import os

scripts = [
    "generate_core_entities.py",
    "generate_trips_schedules.py",
    "generate_passengers_tickets.py",
    "generate_passenger_counts.py",
    "generate_delays_gps.py",
    "inject_noise.py"
]

def main():
    print("Starting UrbanTransit IQ Data Generation...")
    start_time = time.time()
    
    # Clean old files
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "raw_data")
    if os.path.exists(raw_dir):
        for f in os.listdir(raw_dir):
            if f.endswith(".csv"):
                os.remove(os.path.join(raw_dir, f))
                
    for script in scripts:
        print(f"\n[{time.strftime('%H:%M:%S')}] Running {script}...")
        script_path = os.path.join(os.path.dirname(__file__), script)
        subprocess.run(["python", script_path], check=True)
        
    duration = time.time() - start_time
    print(f"\n[SUCCESS] Data generation complete in {duration/60:.2f} minutes.")
    print("Run python data_generator/verify_minimums.py to lock requirements.")

if __name__ == "__main__":
    main()
