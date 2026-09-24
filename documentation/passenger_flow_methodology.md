# Passenger Flow Methodology

This document outlines how the Origin-Destination (OD) pairs are inferred from the transit datasets.

### Methodology
1. **Ticket Sequences:** Tickets are joined with `passenger_counts` on `trip_id` and `stop_id`.
2. **GPS Matching:** When ticket tap-on and tap-off data is missing, we infer the destination by looking at the passenger's *next* ticket tap-in, calculating the closest stop to their historical travel patterns.
3. **Matrix Generation:** The resulting pairs are aggregated into an OD matrix with the following dimensions: `origin_stop`, `destination_stop`, `time_period`, and `day_type`.

This ensures the peak flow periods are dynamically calculated based on true demand, not hardcoded hours.
