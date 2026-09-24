-- spark_sql/joins.sql
-- Phase 4: Data Integration (Joins)
-- Maps to SRS: Step 6

-- Note: These views should be executed sequentially in Spark to build the master dataset.

-- 1. Route & Stops integration
CREATE OR REPLACE TEMPORARY VIEW route_stops_enhanced AS
SELECT rs.*, s.stop_name, s.lat, s.lon, r.route_name, r.route_type
FROM clean_route_stops rs
JOIN clean_stops s ON rs.stop_id = s.stop_id
JOIN clean_routes r ON rs.route_id = r.route_id;

-- 2. Trips & Vehicles
CREATE OR REPLACE TEMPORARY VIEW trips_enhanced AS
SELECT t.*, v.capacity, v.vehicle_type
FROM clean_trips t
LEFT JOIN clean_vehicles v ON t.vehicle_id = v.vehicle_id;

-- 3. Passenger Counts with Stops
CREATE OR REPLACE TEMPORARY VIEW trip_passenger_flow AS
SELECT pc.*, rse.stop_name, rse.lat, rse.lon
FROM clean_passenger_counts pc
JOIN route_stops_enhanced rse 
  ON pc.stop_id = rse.stop_id AND pc.trip_id IN (SELECT trip_id FROM clean_trips WHERE route_id = rse.route_id);

-- 4. Trips with Delays
CREATE OR REPLACE TEMPORARY VIEW trip_delays AS
SELECT t.trip_id, sum(d.delay_minutes) as total_delay_minutes
FROM clean_trips t
LEFT JOIN clean_delays d ON t.trip_id = d.trip_id
GROUP BY t.trip_id;

-- 5. Master Trip Table (trip_master)
CREATE OR REPLACE TEMPORARY VIEW trip_master AS
SELECT 
    t.trip_id,
    t.route_id,
    t.vehicle_id,
    t.capacity,
    t.start_time as scheduled_start,
    t.end_time as scheduled_end,
    d.total_delay_minutes,
    t.direction
FROM trips_enhanced t
LEFT JOIN trip_delays d ON t.trip_id = d.trip_id;
