# Recommendation Priority Logic

Priority levels (Low, Medium, High, Critical) are assigned dynamically to operational recommendations based on the severity of the metrics observed.

### Logic Rules:
1. **Critical:** Assigned if the route's `average_occupancy_pct` exceeds 110%. This indicates severe overcrowding requiring immediate capacity injection.
2. **High:** Assigned if `average_occupancy_pct` is between 85% and 110%, or if severe bunching events are detected on high-demand corridors.
3. **Medium:** Assigned for underutilization. If `average_occupancy_pct` drops below 20%, it causes financial bleed and warrants review, but is not an immediate passenger safety issue.
4. **Low:** Assigned to schedule optimization tweaks (e.g. minor mismatches) where performance is already acceptable but could be slightly improved.
