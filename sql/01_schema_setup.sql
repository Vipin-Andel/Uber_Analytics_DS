-- 1. Database Creation (Run separately if needed)
-- CREATE DATABASE uber_analytics;

-- 2. Drop table if exists
DROP TABLE IF EXISTS uber_trips;

-- 3. Create main trips table
CREATE TABLE uber_trips (
    ride_pk SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME NOT NULL,
    booking_id VARCHAR(20) NOT NULL,
    booking_status VARCHAR(50) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL,
    pickup_location VARCHAR(100) NOT NULL,
    drop_location VARCHAR(100) NOT NULL,
    cancelled_rides_by_customer NUMERIC(3, 1),
    reason_for_cancelling_by_customer VARCHAR(150),
    cancelled_rides_by_driver NUMERIC(3, 1),
    driver_cancellation_reason VARCHAR(150),
    incomplete_rides NUMERIC(3, 1),
    incomplete_rides_reason VARCHAR(150),
    booking_value NUMERIC(10, 2),
    ride_distance NUMERIC(10, 2),
    driver_ratings NUMERIC(3, 2),
    customer_rating NUMERIC(3, 2),
    payment_method VARCHAR(50)
);

-- 4. Create Indexes for High Performance Querying
CREATE INDEX idx_uber_booking_status ON uber_trips(booking_status);
CREATE INDEX idx_uber_customer_id ON uber_trips(customer_id);
CREATE INDEX idx_uber_vehicle_type ON uber_trips(vehicle_type);
CREATE INDEX idx_uber_pickup_location ON uber_trips(pickup_location);
CREATE INDEX idx_uber_date ON uber_trips(date);
CREATE INDEX idx_uber_composite_booking ON uber_trips(booking_id, date, time);
