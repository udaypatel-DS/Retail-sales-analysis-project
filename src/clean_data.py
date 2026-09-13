"""
clean_data.py
-------------
Takes the raw, messy export (data/raw_sales_data.csv) and produces an
analysis-ready file (data/cleaned_sales_data.csv).

Cleaning steps performed:
1. Standardize text columns (trim whitespace, fix casing)
2. Remove duplicate orders
3. Fix negative/invalid units_sold values
4. Handle missing values (impute where sensible, drop where not)
5. Recalculate revenue wherever price or units were originally missing
6. Add a few derived columns useful for analysis (month, quarter)
"""

import pandas as pd
import numpy as np

RAW_PATH = "/home/claude/retail-sales-analysis/data/raw_sales_data.csv"
CLEAN_PATH = "/home/claude/retail-sales-analysis/data/cleaned_sales_data.csv"

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["order_date"])
    return df

def clean(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    # 1. Standardize text fields
    text_cols = ["region", "category", "product_name", "customer_segment", "payment_mode"]
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip().str.title()
        df[col] = df[col].replace("Nan", np.nan)

    # 2. Drop exact duplicate rows (same order_id = same order exported twice)
    df = df.drop_duplicates(subset="order_id", keep="first")

    # 3. Fix negative units_sold (data-entry sign errors) -> take absolute value
    df["units_sold"] = df["units_sold"].abs()

    # 4. Impute missing categorical values with "Unknown" so no rows are silently lost
    for col in ["customer_segment", "payment_mode"]:
        df[col] = df[col].fillna("Unknown")

    # 5. Impute missing unit_price with the median price for that product
    df["unit_price"] = df.groupby("product_name")["unit_price"].transform(
        lambda x: x.fillna(x.median())
    )

    # 6. Impute missing units_sold with the median units for that category
    df["units_sold"] = df.groupby("category")["units_sold"].transform(
        lambda x: x.fillna(x.median())
    )

    # 7. Recompute revenue wherever it's missing or inconsistent with price * units
    df["revenue"] = (df["units_sold"] * df["unit_price"]).round(2)

    # 8. Drop any row still missing a core field after imputation (very rare)
    df = df.dropna(subset=["order_date", "units_sold", "unit_price", "revenue"])

    # 9. Derived time columns for easier trend analysis
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    df["quarter"] = df["order_date"].dt.to_period("Q").astype(str)

    after = len(df)
    print(f"Cleaning complete: {before} raw rows -> {after} clean rows "
          f"({before - after} removed as duplicates/unrecoverable)")

    return df.reset_index(drop=True)


if __name__ == "__main__":
    raw_df = load_data(RAW_PATH)
    clean_df = clean(raw_df)
    clean_df.to_csv(CLEAN_PATH, index=False)
    print(f"Saved cleaned data to {CLEAN_PATH}")
