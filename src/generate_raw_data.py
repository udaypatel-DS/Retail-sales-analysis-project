"""
generate_raw_data.py
---------------------
Generates a synthetic, intentionally "messy" retail sales dataset so the
project can demonstrate real data-cleaning work (missing values, duplicate
rows, inconsistent text casing, stray whitespace, and a few bad numbers).

Run this once to (re)create data/raw_sales_data.csv.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

REGIONS = ["North", "South", "East", "West", "Central"]
CATEGORIES = {
    "Electronics": ["Wireless Earbuds", "Bluetooth Speaker", "Smart Watch", "Power Bank", "USB-C Cable"],
    "Home & Kitchen": ["Non-Stick Pan", "Electric Kettle", "Mixer Grinder", "LED Lamp", "Storage Rack"],
    "Fashion": ["Cotton T-Shirt", "Denim Jeans", "Running Shoes", "Formal Shirt", "Backpack"],
    "Grocery": ["Basmati Rice 5kg", "Cooking Oil 1L", "Green Tea Pack", "Atta 10kg", "Spice Combo"],
    "Beauty": ["Face Wash", "Sunscreen SPF50", "Shampoo 340ml", "Lip Balm", "Hair Serum"],
}
SEGMENTS = ["Retail", "Wholesale", "Online"]
PAYMENTS = ["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"]

n_rows = 1200
dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")

rows = []
for i in range(n_rows):
    date = np.random.choice(dates)
    category = np.random.choice(list(CATEGORIES.keys()))
    product = np.random.choice(CATEGORIES[category])
    region = np.random.choice(REGIONS)
    segment = np.random.choice(SEGMENTS)
    payment = np.random.choice(PAYMENTS)
    units = np.random.randint(1, 40)

    base_prices = {
        "Electronics": (800, 4500), "Home & Kitchen": (400, 3000),
        "Fashion": (300, 2200), "Grocery": (120, 900), "Beauty": (150, 1200),
    }
    lo, hi = base_prices[category]
    unit_price = round(np.random.uniform(lo, hi), 2)
    revenue = round(units * unit_price, 2)

    rows.append({
        "order_id": f"ORD{10000+i}",
        "order_date": date,
        "region": region,
        "category": category,
        "product_name": product,
        "customer_segment": segment,
        "payment_mode": payment,
        "units_sold": units,
        "unit_price": unit_price,
        "revenue": revenue,
    })

df = pd.DataFrame(rows)

# --- Introduce realistic messiness ---

# 1. Inconsistent casing / stray whitespace in text columns
messy_idx = df.sample(frac=0.15, random_state=1).index
df.loc[messy_idx, "region"] = df.loc[messy_idx, "region"].str.upper()
messy_idx2 = df.sample(frac=0.1, random_state=2).index
df.loc[messy_idx2, "category"] = df.loc[messy_idx2, "category"].apply(lambda x: f"  {x.lower()} ")

# 2. Missing values scattered across a few columns
for col, frac in [("unit_price", 0.03), ("units_sold", 0.02), ("customer_segment", 0.04), ("payment_mode", 0.03)]:
    idx = df.sample(frac=frac, random_state=3).index
    df.loc[idx, col] = np.nan

# 3. A handful of duplicate rows (as if the export ran twice)
dupes = df.sample(n=25, random_state=4)
df = pd.concat([df, dupes], ignore_index=True)

# 4. A few negative / clearly bad values (data entry errors)
bad_idx = df.sample(n=8, random_state=5).index
df.loc[bad_idx, "units_sold"] = -df.loc[bad_idx, "units_sold"]

# 5. revenue left un-recalculated for missing rows (so cleaning script has real work to do)
df.loc[df["unit_price"].isna() | df["units_sold"].isna(), "revenue"] = np.nan

df = df.sample(frac=1, random_state=6).reset_index(drop=True)  # shuffle rows
df.to_csv("/home/claude/retail-sales-analysis/data/raw_sales_data.csv", index=False)
print(f"raw_sales_data.csv written with {len(df)} rows")
