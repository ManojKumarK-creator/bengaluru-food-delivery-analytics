import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

# 1. Generate Customers (800 unique customers)
localities = [
    "Jayanagar", "Bannerghatta Road", "Koramangala", "Indiranagar",
    "Whitefield", "Electronic City", "HSR Layout", "JP Nagar", "BTM Layout"
]

customers = []
for cid in range(1001, 1801):
    customers.append({
        "customer_id": cid,
        "home_locality": random.choice(localities),
        "signup_date": (datetime(2025, 1, 1) + timedelta(days=random.randint(0, 300))).strftime("%Y-%m-%d"),
        "membership_tier": np.random.choice(["Regular", "Plus", "Pro"], p=[0.65, 0.25, 0.10])
    })
df_customers = pd.DataFrame(customers)

# 2. Generate Restaurants (60 outlets across Bengaluru)
cuisines = ["North Indian", "South Indian", "Biryani", "Pizza & Fast Food", "Chinese", "Healthy & Salads"]
restaurants = []
for rid in range(201, 261):
    loc = random.choice(localities)
    cuisine = random.choice(cuisines)
    restaurants.append({
        "restaurant_id": rid,
        "restaurant_name": f"{loc.split()[0]} {cuisine.split()[0]} Kitchen #{rid}",
        "locality": loc,
        "cuisine": cuisine,
        "avg_prep_mins": random.randint(12, 28)
    })
df_restaurants = pd.DataFrame(restaurants)

# 3. Generate 5,000 Orders with realistic patterns + intentional dirty data
orders = []
start_date = datetime(2026, 1, 1)

# Dirty locality variations to clean later in Pandas
dirty_loc_map = {
    "Bannerghatta Road": ["Bannerghatta Road", "Bannerghatta Rd", "bannerghatta road"],
    "Electronic City": ["Electronic City", "E-City", "Electronic city"],
    "HSR Layout": ["HSR Layout", "HSR", "hsr layout"]
}

for oid in range(50001, 55001):
    cust = df_customers.sample(1).iloc[0]
    rest = df_restaurants.sample(1).iloc[0]
    
    # Peak lunch (12-14) and dinner (19-22) weighting
    hour = np.random.choice(
        list(range(8, 24)),
        p=[0.02, 0.03, 0.03, 0.04, 0.11, 0.13, 0.08, 0.04, 0.04, 0.05, 0.06, 0.10, 0.13, 0.09, 0.03, 0.02]
    )
    order_dt = start_date + timedelta(days=random.randint(0, 180), hours=int(hour), minutes=random.randint(0, 59))
    
    base_amount = round(np.random.uniform(180, 950), 2)
    promo_used = np.random.choice(["NONE", "BLR50", "FEAST20", "PROFREE"], p=[0.45, 0.25, 0.20, 0.10])
    
    discount = 0.0
    if promo_used == "BLR50":
        discount = 50.0
    elif promo_used == "FEAST20":
        discount = round(base_amount * 0.20, 2)
    elif promo_used == "PROFREE" and cust["membership_tier"] != "Regular":
        discount = 40.0
        
    # Traffic delay simulation for Outer Ring Road / Whitefield / E-City during peak hours
    is_peak = hour in [12, 13, 19, 20, 21]
    traffic_delay = random.randint(8, 22) if (is_peak and rest["locality"] in ["Whitefield", "Electronic City", "Koramangala"]) else random.randint(0, 8)
    
    promised_mins = 35
    actual_mins = rest["avg_prep_mins"] + random.randint(10, 18) + traffic_delay
    
    # Inject ~5% missing ratings & ~3% negative/outlier delivery anomalies
    rating = round(np.random.uniform(3.2, 5.0), 1) if actual_mins <= 45 else round(np.random.uniform(1.8, 3.8), 1)
    if random.random() < 0.05:
        rating = np.nan
        
    raw_loc = rest["locality"]
    if raw_loc in dirty_loc_map:
        raw_loc = random.choice(dirty_loc_map[raw_loc])
        
    orders.append({
        "order_id": oid,
        "customer_id": cust["customer_id"],
        "restaurant_id": rest["restaurant_id"],
        "delivery_locality": raw_loc,
        "order_timestamp": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "order_amount": base_amount,
        "discount_amount": discount,
        "promo_code": promo_used,
        "promised_mins": promised_mins,
        "actual_delivery_mins": actual_mins,
        "customer_rating": rating,
        "order_status": np.random.choice(["Delivered", "Cancelled"], p=[0.94, 0.06])
    })

df_orders = pd.DataFrame(orders)

# Inject 35 exact duplicate rows to demonstrate deduplication in Python
duplicates = df_orders.sample(35, random_state=42)
df_orders = pd.concat([df_orders, duplicates], ignore_index=True)

# Save to CSV
df_customers.to_csv("data/customers.csv", index=False)
df_restaurants.to_csv("data/restaurants.csv", index=False)
df_orders.to_csv("data/raw_orders.csv", index=False)

print("Datasets generated successfully!")
print(f"Customers: {len(df_customers)}, Restaurants: {len(df_restaurants)}, Raw Orders: {len(df_orders)}")