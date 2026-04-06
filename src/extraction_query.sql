/*
BUSINESS CONTEXT:
We need to extract a clean, user-level dataset to analyze the 'Promotional UI Banner' A/B test.
To avoid skewed data from users logging in multiple times, we only capture their *first* exposure 
to the experiment, and we tie it to any orders placed during that specific session.
*/

WITH first_exposure AS (
    -- 1. WINDOW FUNCTION: Isolate the first time a user was exposed to the UI test
    SELECT 
        session_id,
        user_id,
        timestamp AS exposure_time,
        variant,
        ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY timestamp ASC) as session_rank
    FROM 
        experiments
    WHERE 
        timestamp >= '2026-03-24' -- Start date of the A/B test
),

session_orders AS (
    -- 2. AGGREGATION: Summarize order totals per session 
    SELECT 
        session_id,
        COUNT(order_id) as total_orders,
        SUM(order_amount) as total_order_value
    FROM 
        orders
    GROUP BY 
        session_id
)

-- 3. FINAL JOIN: Combine demographics, experiment variant, and checkout behavior
SELECT 
    u.user_id,
    u.primary_location,
    e.variant,
    e.exposure_time,
    -- Create a binary conversion metric (1 if they ordered, 0 if they didn't)
    CASE WHEN o.total_orders > 0 THEN 1 ELSE 0 END AS checkout_completed,
    COALESCE(o.total_order_value, 0) AS total_spend
FROM 
    first_exposure e
JOIN 
    users u ON e.user_id = u.user_id
LEFT JOIN 
    session_orders o ON e.session_id = o.session_id
WHERE 
    e.session_rank = 1; -- Crucial filter: Only look at their very first session in the test