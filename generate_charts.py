import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Create visuals subfolder if it doesn't exist
os.makedirs("visuals", exist_ok=True)

# Load cleaned data
df = pd.read_csv("data/cleaned_orders.csv")
df_restaurants = pd.read_csv("data/restaurants.csv")
df = df.merge(df_restaurants[["restaurant_id", "cuisine"]], on="restaurant_id", how="left")

# Set clean visual style
sns.set_theme(style="whitegrid")

# ---------------------------------------------------------
# CHART 1: Order Volume Heatmap (Day of Week vs. Hour)
# ---------------------------------------------------------
days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heatmap_data = df.pivot_table(index="day_of_week", columns="order_hour", values="order_id", aggfunc="count").reindex(days_order)

plt.figure(figsize=(12, 5))
sns.heatmap(heatmap_data, cmap="YlOrRd", annot=True, fmt="g", cbar_kws={"label": "Order Count"})
plt.title("Bengaluru Food Delivery Demand: Day of Week vs. Hour", fontsize=14, fontweight="bold")
plt.xlabel("Hour of Day (24-Hour Format)")
plt.ylabel("Day of Week")
plt.tight_layout()
plt.savefig("visuals/1_peak_hour_heatmap.png", dpi=300)
plt.close()

# ---------------------------------------------------------
# CHART 2: Average Delivery Delay by Bengaluru Locality
# ---------------------------------------------------------
loc_perf = df.groupby("delivery_locality").agg(
    avg_delivery_mins=("actual_delivery_mins", "mean"),
    late_rate=("is_delayed", lambda x: x.mean() * 100)
).sort_values("avg_delivery_mins", ascending=False).reset_index()

plt.figure(figsize=(10, 5))
bars = sns.barplot(data=loc_perf, x="avg_delivery_mins", y="delivery_locality", palette="Reds_r")
plt.axvline(35, color="black", linestyle="--", label="Promised SLA (35 mins)")
plt.title("Average Delivery Time by Bengaluru Locality", fontsize=14, fontweight="bold")
plt.xlabel("Average Delivery Time (Minutes)")
plt.ylabel("Locality")
plt.legend()
plt.tight_layout()
plt.savefig("visuals/2_locality_delivery_times.png", dpi=300)
plt.close()

# ---------------------------------------------------------
# CHART 3: Promo Code Impact on Net Revenue vs. Discount
# ---------------------------------------------------------
promo_perf = df.groupby("promo_code").agg(
    avg_net_revenue=("net_revenue", "mean"),
    avg_discount=("discount_amount", "mean")
).reset_index()

promo_melted = promo_perf.melt(id_vars="promo_code", value_vars=["avg_net_revenue", "avg_discount"],
                               var_name="Metric", value_name="INR")

plt.figure(figsize=(8, 5))
sns.barplot(data=promo_melted, x="promo_code", y="INR", hue="Metric", palette=["#2b5c8f", "#e67e22"])
plt.title("Average Net Revenue vs. Discount Erosion by Promo Code", fontsize=13, fontweight="bold")
plt.xlabel("Promo Code")
plt.ylabel("Amount (INR)")
plt.tight_layout()
plt.savefig("visuals/3_promo_revenue_impact.png", dpi=300)
plt.close()

# ---------------------------------------------------------
# CHART 4: Customer Rating Drop on Delayed vs. On-Time Orders
# ---------------------------------------------------------
df["Delivery Status"] = df["is_delayed"].map({0: "On-Time (<= 35m)", 1: "Delayed (> 35m)"})

plt.figure(figsize=(7, 5))
sns.boxplot(data=df, x="Delivery Status", y="customer_rating", palette=["#2ecc71", "#e74c3c"])
plt.title("Customer Rating Distribution: On-Time vs. Delayed Orders", fontsize=13, fontweight="bold")
plt.xlabel("Delivery SLA Status")
plt.ylabel("Customer Rating (1 to 5)")
plt.tight_layout()
plt.savefig("visuals/4_rating_vs_delay.png", dpi=300)
plt.close()

print("All 4 charts exported successfully into the 'visuals/' folder!")