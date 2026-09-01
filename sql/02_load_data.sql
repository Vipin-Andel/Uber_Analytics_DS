-- Load cleaned CSV data into PostgreSQL
COPY uber_trips (
    date,
    time,
    booking_id,
    booking_status,
    customer_id,
    vehicle_type,
    pickup_location,
    drop_location,
    cancelled_rides_by_customer,
    reason_for_cancelling_by_customer,
    cancelled_rides_by_driver,
    driver_cancellation_reason,
    incomplete_rides,
    incomplete_rides_reason,
    booking_value,
    ride_distance,
    driver_ratings,
    customer_rating,
    payment_method
)
FROM 'F:/Projects/Uber_Analytics_DS/data/processed/uber_cleaned.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Sanity Check Count
SELECT COUNT(*) AS total_loaded_records FROM uber_trips;