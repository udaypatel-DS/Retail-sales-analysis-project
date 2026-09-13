-- ============================================================
-- sales_queries.sql
-- Analysis queries written against the `sales` table
-- (loaded from data/cleaned_sales_data.csv into SQLite/any RDBMS)
-- ============================================================

-- 1. Total revenue, orders, and average order value
SELECT
    COUNT(*)                       AS total_orders,
    SUM(revenue)                   AS total_revenue,
    ROUND(AVG(revenue), 2)         AS avg_order_value
FROM sales;

-- 2. Monthly revenue trend
SELECT
    month,
    SUM(revenue) AS monthly_revenue,
    COUNT(*)     AS orders
FROM sales
GROUP BY month
ORDER BY month;

-- 3. Revenue and order count by region, ranked highest to lowest
SELECT
    region,
    SUM(revenue)  AS total_revenue,
    COUNT(*)      AS total_orders,
    ROUND(SUM(revenue) * 100.0 / (SELECT SUM(revenue) FROM sales), 2) AS pct_of_total
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;

-- 4. Top 10 products by revenue
SELECT
    product_name,
    category,
    SUM(units_sold) AS total_units_sold,
    SUM(revenue)     AS total_revenue
FROM sales
GROUP BY product_name, category
ORDER BY total_revenue DESC
LIMIT 10;

-- 5. Category performance with average order value
SELECT
    category,
    COUNT(*)                  AS total_orders,
    SUM(revenue)               AS total_revenue,
    ROUND(AVG(revenue), 2)      AS avg_order_value
FROM sales
GROUP BY category
ORDER BY total_revenue DESC;

-- 6. Customer segment contribution to revenue
SELECT
    customer_segment,
    SUM(revenue) AS total_revenue,
    ROUND(SUM(revenue) * 100.0 / (SELECT SUM(revenue) FROM sales), 2) AS pct_of_total
FROM sales
GROUP BY customer_segment
ORDER BY total_revenue DESC;

-- 7. Preferred payment mode by region (which region uses which payment mode most)
SELECT
    region,
    payment_mode,
    COUNT(*) AS order_count
FROM sales
GROUP BY region, payment_mode
ORDER BY region, order_count DESC;

-- 8. Month-over-month revenue growth (%) using a window function
SELECT
    month,
    monthly_revenue,
    ROUND(
        (monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY month)) * 100.0
        / LAG(monthly_revenue) OVER (ORDER BY month), 2
    ) AS mom_growth_pct
FROM (
    SELECT month, SUM(revenue) AS monthly_revenue
    FROM sales
    GROUP BY month
);

-- 9. Best-performing product per region (using a window function to rank)
SELECT region, product_name, total_revenue
FROM (
    SELECT
        region,
        product_name,
        SUM(revenue) AS total_revenue,
        RANK() OVER (PARTITION BY region ORDER BY SUM(revenue) DESC) AS rnk
    FROM sales
    GROUP BY region, product_name
)
WHERE rnk = 1;
