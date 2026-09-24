# Tricky Route Cases Handling

As requested by the SRS (Step 16), the following edge cases are explicitly handled in our pipeline:

1. **High-demand route with poor punctuality:** Addressed in `11_route_performance_score.py`. The route classification logic explicitly checks `(avg_demand > 50) & (avg_delay > 15)` and outputs "High Demand, but Unreliable".
2. **Low-demand route with excellent punctuality:** Handled in classification via `(avg_occupancy < 30) & (performance_score >= 75)` which assigns "Reliable, but Underutilized".
3. **Profitable/necessary route with low occupancy (feeder routes):** Handled in `10_underutilization.py`. We require BOTH low occupancy (<20%) AND low raw volume (<10 passengers/trip) before flagging it, preventing false positives on necessary feeder routes.
4. **Route overcrowded only in one direction:** Addressed in `09_persistent_overcrowding.py`. GroupBy operates on `("route_id", "direction")`, tracking overcrowding distinctively for inbound vs outbound.
5. **Route overcrowded only at specific stops:** `08_overcrowding_detection.py` processes trip segment-level capacities before aggregating, ensuring partial route crowding is flagged.
6. **High passenger count from ONE major event:** Will be handled in Phase 9 (`special_event_detection.py`), marking extreme statistical outliers to exclude them from standard baseline scoring.
7. **Delay caused by one abnormal day:** Performance score uses overall average delays and penalties across the dataset window rather than single worst-day metrics. (Future update will shift to medians).
8. **Route good on weekdays, poor on weekends:** Features are generated per trip and time period, allowing separate breakdown queries in the dashboard (Phase 12).
9. **High demand but excess frequency:** Gap analysis (Phase 9) handles this by comparing raw passenger throughput to theoretical capacity (vehicles * capacity * frequency).
10. **Low demand due to schedule mismatch:** Will be tackled in OD Matrix & Peak period comparisons vs actual schedule times in Phase 10.
