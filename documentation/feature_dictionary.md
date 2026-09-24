# Feature Dictionary (Phase 4)

This dictionary details the engineered features available in `trip_features.parquet`.

| Feature Name | Type | Description | Source Columns / Logic |
|---|---|---|---|
| `total_delay_minutes` | Float | Sum of all delays for a trip | Derived from `delays.delay_minutes` |
| `total_boardings` | Int | Total passengers boarded on trip | Sum of `passenger_counts.boarding_count` |
| `max_occupancy` | Int | Peak number of passengers onboard | Max of `passenger_counts.occupancy` |
| `vehicle_occupancy_pct` | Float | Percentage of vehicle capacity used | `(max_occupancy / vehicles.capacity) * 100` |
| `overcrowded_flag` | Int (0/1) | Indicates if occupancy exceeded 100% | `1 if vehicle_occupancy_pct > 100 else 0` |
| `scheduled_travel_time_min`| Float | Total scheduled trip duration in mins | `end_time - start_time` |
| `is_delayed` | Int (0/1) | Flag if trip was delayed > 5 mins | `1 if total_delay_minutes > 5 else 0` |
| `rolling_route_occupancy` | Float | Trailing average route occupancy | Window function: average of previous 7 trips on route |
