from recommendation_engine.03_whatif_simulator import simulate_scenario

def evaluate_impact(route_id, current_demand, current_freq, new_freq, current_cap, new_cap, demand_multiplier):
    # This wraps the simulator to provide higher-level KPI impacts.
    
    sim = simulate_scenario(route_id, current_freq, new_freq, current_cap, new_cap, demand_multiplier)
    
    # Calculate overcrowding risk
    new_demand = current_demand * demand_multiplier
    new_capacity = sim["estimated_impacts"]["estimated_daily_capacity"]
    
    est_occupancy_pct = (new_demand / new_capacity) * 100 if new_capacity > 0 else 999
    
    risk_level = "High" if est_occupancy_pct > 100 else "Medium" if est_occupancy_pct > 80 else "Low"
    
    sim["estimated_impacts"]["estimated_occupancy_pct"] = round(est_occupancy_pct, 1)
    sim["estimated_impacts"]["estimated_crowding_risk"] = risk_level
    
    return sim

if __name__ == "__main__":
    print("Scenario Impact Module Loaded.")
    # Example: Demand grows 20%, we increase trips from 20 to 30.
    res = evaluate_impact("R12", 1500, 20, 30, 50, 50, 1.2)
    print(res)
