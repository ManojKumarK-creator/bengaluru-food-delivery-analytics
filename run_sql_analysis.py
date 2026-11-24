import sqlite3
import pandas as pd

# 1. Create a local SQLite database file (no server needed)
conn = sqlite3.connect("data/blr_food_delivery.db")

# 2. Load all 3 CSV files into SQL tables
pd.read_csv("data/customers.csv").to_sql("customers", conn, if_exists="replace", index=False)
pd.read_csv("data/restaurants.csv").to_sql("restaurants", conn, if_exists="replace", index=False)
pd.read_csv("data/cleaned_orders.csv").to_sql("orders", conn, if_exists="replace", index=False)

print("SQLite database 'blr_food_delivery.db' created successfully!\n")

# Helper function to execute SQL and print clean DataFrames
def run_query(title, query):
    print(f"=== {title} ===")
    result = pd.read_sql_query(query, conn)
    print(result.to_string(index=False))
    print("\n" + "-" * 60 + "\n")

# Query 1: Overall Business KPIs
run_query("1. OVERALL BUSINESS KPIS", """
SELECT 
    COUNT(order_id) AS total_delivered_orders,
    ROUND(SUM(order_amount), 2) AS gross_revenue,
    ROUND(SUM(discount_amount), 2) AS total_discounts,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(AVG(net_revenue), 2) AS avg_order_value,
    ROUND(AVG(customer_rating), 2) AS avg_rating
FROM orders
WHERE order_status = 'Delivered';
""")

# Query 2: Bengaluru Locality SLA & Delay Bottlenecks
run_query("2. LOCALITY DELIVERY DELAY BOTTLENECKS", """
SELECT 
    delivery_locality,
    COUNT(*) AS total_orders,
    ROUND(AVG(actual_delivery_mins), 1) AS avg_delivery_mins,
    ROUND(SUM(is_delayed) * 100.0 / COUNT(*), 1) AS late_delivery_pct,
    ROUND(AVG(customer_rating), 2) AS avg_rating
FROM orders
WHERE order_status = 'Delivered'
GROUP BY delivery_locality
ORDER BY late_delivery_pct DESC;
""")

# Query 3: Top 3 Revenue Cuisines per Locality (Window Function: DENSE_RANK)
run_query("3. TOP 3 CUISINES PER LOCALITY (WINDOW FUNCTION)", """
WITH CuisineRevenue AS (
    SELECT 
        r.locality,
        r.cuisine,
        COUNT(o.order_id) AS total_orders,
        ROUND(SUM(o.net_revenue), 2) AS total_net_revenue,
        DENSE_RANK() OVER (PARTITION BY r.locality ORDER BY SUM(o.net_revenue) DESC) AS revenue_rank
    FROM orders o
    JOIN restaurants r ON o.restaurant_id = r.restaurant_id
    WHERE o.order_status = 'Delivered'
    GROUP BY r.locality, r.cuisine
)
SELECT locality, revenue_rank, cuisine, total_orders, total_net_revenue
FROM CuisineRevenue
WHERE revenue_rank <= 3
ORDER BY locality, revenue_rank;
""")

# Query 4: Promo Code Margin Erosion
run_query("4. PROMO CODE MARGIN IMPACT", """
SELECT 
    promo_code,
    COUNT(*) AS orders_count,
    ROUND(AVG(order_amount), 2) AS avg_gross_order,
    ROUND(AVG(discount_amount), 2) AS avg_discount,
    ROUND(AVG(net_revenue), 2) AS avg_net_revenue
FROM orders
WHERE order_status = 'Delivered'
GROUP BY promo_code
ORDER BY orders_count DESC;
""")

# Query 5: Customer Retention Segmentation (CTE)
run_query("5. CUSTOMER RETENTION SEGMENTATION", """
WITH CustomerOrderCounts AS (
    SELECT 
        c.customer_id,
        COUNT(o.order_id) AS order_count,
        ROUND(SUM(COALESCE(o.net_revenue, 0)), 2) AS lifetime_spend
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.order_status = 'Delivered'
    GROUP BY c.customer_id
)
SELECT 
    CASE 
        WHEN order_count = 0 THEN '0 Orders (Inactive)'
        WHEN order_count = 1 THEN '1 Order (One-Time)'
        WHEN order_count BETWEEN 2 AND 4 THEN '2-4 Orders (Occasional)'
        ELSE '5+ Orders (Loyal Repeat)'
    END AS customer_segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(lifetime_spend), 2) AS avg_lifetime_spend
FROM CustomerOrderCounts
GROUP BY customer_segment
ORDER BY customer_count DESC;
""")

conn.close()