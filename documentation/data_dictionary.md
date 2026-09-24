# Data Dictionary

## 1. routes.csv
- **route_id**: String, Primary Key
- **route_name**: String, Route display name
- **direction**: String, Direction of travel
- **distance_km**: Float, Total route distance
- **status**: String, Active/Inactive/Maintenance

## 2. stops.csv
- **stop_id**: String, Primary Key
- **stop_name**: String, Name of the stop
- **latitude**: Float, Geo coordinates
- **longitude**: Float, Geo coordinates

## 3. vehicles.csv
- **vehicle_id**: String, Primary Key
- **type**: String, Bus/Tram/Subway
- **capacity**: Integer, Max passengers
- **status**: String, Active/Maintenance

*(Draft: Further tables will be elaborated in Phase 13/14 as per prompt)*
