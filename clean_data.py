import pandas as pd
import numpy as np

# 1. Load raw data
df_orders = pd.read_csv("data/raw_orders.csv")
print(f"Raw orders count: {len(df_orders)}")

# 2. Remove exact duplicate orders
df_orders = df_orders.drop_duplicates(subset=["order_id"], keep="first")
print(f"After removing duplicates: {len(df_orders)}")

# 3. Standardize inconsistent Bengaluru locality names
locality_fix = {
    "Bannerghatta Rd": "Bannerghatta Road",
    "bannerghatta road": "Bannerghatta Road",
    "E-City": "Electronic City",
    "Electronic city": "Electronic City",
    "HSR": "HSR Layout",
    "hsr layout": "HSR Layout"
}
df_orders["delivery_locality"] = df_orders["delivery_locality"].replace(locality_fix)

# 4. Convert timestamp to datetime and extract analytical features
df_orders["order_timestamp"] = pd.to_datetime(df_orders["order_timestamp"])
df_orders["order_hour"] = df_orders["order_timestamp"].dt.hour
df_orders["day_of_week"] = df_orders["order_timestamp"].dt.day_name()

# 5. Engineer financial & operational KPIs
df_orders["net_revenue"] = (df_orders["order_amount"] - df_orders["discount_amount"]).round(2)
df_orders["delay_mins"] = df_orders["actual_delivery_mins"] - df_orders["promised_mins"]
df_orders["is_delayed"] = np.where(df_orders["delay_mins"] > 0, 1, 0)

# 6. Handle missing ratings (fill with median rating per locality)
df_orders["customer_rating"] = df_orders.groupby("delivery_locality")["customer_rating"].transform(
    lambda x: x.fillna(round(x.median(), 1))
)

# 7. Save cleaned dataset
df_orders.to_csv("data/cleaned_orders.csv", index=False)
print("Saved cleaned_orders.csv successfully!")
print("\nSummary Metrics:")
print(f"Total Net Revenue: INR {df_orders['net_revenue'].sum():,.2f}")
print(f"Late Delivery Rate: {df_orders['is_delayed'].mean() * 100:.1f}%")
print(f"Average Customer Rating: {df_orders['customer_rating'].mean():.2f} / 5.0")