def simulate_scenario(route_id, current_freq, new_freq, current_capacity, new_capacity, demand_multiplier):
    """
    What-If Simulator Engine.
    Inputs:
    - route_id: string
    - current_freq: trips per day
    - new_freq: proposed trips per day
    - current_capacity: total seats per trip
    - new_capacity: proposed seats per trip
    - demand_multiplier: e.g. 1.2 for 20% demand growth
    """
    # Baseline calculations
    base_daily_capacity = current_freq * current_capacity
    
    # New calculations
    simulated_daily_capacity = new_freq * new_capacity
    
    # Impact on waiting time (simplified: 600 mins operating time / freq)
    base_wait_time = 600 / current_freq if current_freq > 0 else 0
    sim_wait_time = 600 / new_freq if new_freq > 0 else 0
    
    return {
        "route_id": route_id,
        "scenario_inputs": {
            "new_frequency": new_freq,
            "new_capacity": new_capacity,
            "demand_multiplier": demand_multiplier
        },
        "estimated_impacts": {
            "estimated_daily_capacity": simulated_daily_capacity,
            "estimated_wait_time_mins": round(sim_wait_time, 1),
            "estimated_capacity_change_pct": round(((simulated_daily_capacity - base_daily_capacity)/base_daily_capacity)*100, 1) if base_daily_capacity > 0 else 0
        }
    }

if __name__ == "__main__":
    print("What-If Simulator Module Loaded.")
    res = simulate_scenario("R12", 20, 30, 50, 50, 1.0)
    print(res)
