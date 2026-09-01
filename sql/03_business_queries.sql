-- ==========================================================
-- UBER MOBILITY INTELLIGENCE - BUSINESS ANALYTICS SCRIPT
-- ==========================================================

-- 1. Fulfillment & Gross Revenue Health
SELECT 
    booking_status,
    COUNT(*) AS total_bookings,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_share
FROM uber_trips
GROUP BY booking_status
ORDER BY total_bookings DESC;


-- 2. Vehicle Tier Matrix
SELECT 
    vehicle_type,
    COUNT(*) AS total_requests,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS demand_share_pct,
    COUNT(*) FILTER (WHERE booking_status = 'Completed') AS completed_trips,
    ROUND(COUNT(*) FILTER (WHERE booking_status = 'Completed') * 100.0 / COUNT(*), 2) AS completion_rate_pct,
    ROUND(COUNT(*) FILTER (WHERE booking_status = 'Cancelled by Driver') * 100.0 / COUNT(*), 2) AS driver_cancel_rate_pct,
    ROUND(COUNT(*) FILTER (WHERE booking_status = 'No Driver Found') * 100.0 / COUNT(*), 2) AS no_driver_found_pct,
    ROUND(SUM(booking_value), 2) AS total_revenue
FROM uber_trips
GROUP BY vehicle_type
ORDER BY total_requests DESC;


-- 3. Top Demand Pickup Hotspots & Bottlenecks
SELECT 
    pickup_location,
    COUNT(*) AS total_demand,
    COUNT(*) FILTER (WHERE booking_status = 'Completed') AS completed_trips,
    ROUND(COUNT(*) FILTER (WHERE booking_status = 'Completed') * 100.0 / COUNT(*), 2) AS completion_rate_pct,
    ROUND(COUNT(*) FILTER (WHERE booking_status = 'Cancelled by Driver') * 100.0 / COUNT(*), 2) AS driver_cancel_pct,
    ROUND(COUNT(*) FILTER (WHERE booking_status = 'No Driver Found') * 100.0 / COUNT(*), 2) AS no_driver_found_pct
FROM uber_trips
GROUP BY pickup_location
ORDER BY total_demand DESC
LIMIT 10;


-- 4. Customer Frequency Segments
WITH customer_frequency AS (
    SELECT 
        customer_id,
        COUNT(*) AS total_bookings,
        COUNT(*) FILTER (WHERE booking_status = 'Completed') AS completed_bookings,
        COALESCE(SUM(booking_value), 0) AS total_spend
    FROM uber_trips
    GROUP BY customer_id
)
SELECT 
    CASE 
        WHEN total_bookings = 1 THEN '1. One-Time Rider (1 ride)'
        WHEN total_bookings BETWEEN 2 AND 3 THEN '2. Occasional Rider (2-3 rides)'
        WHEN total_bookings BETWEEN 4 AND 6 THEN '3. Regular Rider (4-6 rides)'
        ELSE '4. Power Rider (7+ rides)'
    END AS rider_segment,
    COUNT(*) AS total_customers,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS customer_share_pct,
    SUM(total_bookings) AS total_bookings_generated,
    SUM(completed_bookings) AS total_completed_trips,
    ROUND(SUM(total_spend), 2) AS total_revenue_contribution,
    ROUND(AVG(total_spend), 2) AS avg_spend_per_customer
FROM customer_frequency
GROUP BY 1
ORDER BY 1;


-- 5. Temporal Hourly Demand & Revenue
SELECT 
    EXTRACT(HOUR FROM time) AS ride_hour,
    COUNT(*) AS total_demand,
    COUNT(*) FILTER (WHERE booking_status = 'Completed') AS completed_trips,
    ROUND(COUNT(*) FILTER (WHERE booking_status = 'Completed') * 100.0 / COUNT(*), 2) AS completion_rate_pct,
    ROUND(COUNT(*) FILTER (WHERE booking_status = 'Cancelled by Driver') * 100.0 / COUNT(*), 2) AS driver_cancel_pct,
    ROUND(COUNT(*) FILTER (WHERE booking_status = 'No Driver Found') * 100.0 / COUNT(*), 2) AS no_driver_found_pct,
    ROUND(SUM(booking_value), 2) AS hourly_revenue
FROM uber_trips
GROUP BY 1
ORDER BY total_demand DESC;


-- 6. Payment Channel & Realized Revenue
SELECT 
    payment_method,
    COUNT(*) AS completed_rides,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS payment_share_pct,
    ROUND(SUM(booking_value), 2) AS realized_revenue,
    ROUND(AVG(booking_value), 2) AS avg_ticket_size
FROM uber_trips
WHERE booking_status = 'Completed'
GROUP BY payment_method
ORDER BY completed_rides DESC;


-- 7. Cancellation Root-Cause Deep Dive (Driver vs. Customer)
SELECT 
    'Driver Cancellation' AS cancellation_party,
    driver_cancellation_reason AS failure_reason,
    COUNT(*) AS incident_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY 'Driver Cancellation'), 2) AS pct_within_party
FROM uber_trips
WHERE booking_status = 'Cancelled by Driver'
GROUP BY driver_cancellation_reason

UNION ALL

SELECT 
    'Customer Cancellation' AS cancellation_party,
    reason_for_cancelling_by_customer AS failure_reason,
    COUNT(*) AS incident_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY 'Customer Cancellation'), 2) AS pct_within_party
FROM uber_trips
WHERE booking_status = 'Cancelled by Customer'
GROUP BY reason_for_cancelling_by_customer
ORDER BY cancellation_party, incident_count DESC;