import json

def assign_priority():
    print("Assigning Priorities based on impact...")
    
    # Priority is typically calculated on the fly in the rule engine, 
    # but as requested this script formally applies the logic to existing recommendations.
    
    with open("reports/recommendations.json", "r") as f:
        recs = json.load(f)
        
    for rec in recs:
        # Example logic:
        # High occupancy + high events = Critical
        reason = rec["reason"]
        occ = reason.get("average_occupancy_pct", 0)
        
        if occ > 110:
            rec["priority"] = "Critical"
        elif occ > 85:
            rec["priority"] = "High"
        elif occ < 20:
            rec["priority"] = "Medium" # Financial impact
        else:
            rec["priority"] = "Low"
            
    with open("reports/recommendations.json", "w") as f:
        json.dump(recs, f, indent=4)
        
    print("Priorities re-calculated and assigned.")

if __name__ == "__main__":
    assign_priority()
