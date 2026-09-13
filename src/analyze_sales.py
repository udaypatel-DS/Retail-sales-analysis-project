"""
analyze_sales.py
-----------------
Runs exploratory analysis on the cleaned dataset and saves chart images
to the visuals/ folder. This mirrors the kind of analysis that would
normally feed a Power BI / Excel dashboard.
"""

import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = "/home/claude/retail-sales-analysis/data/cleaned_sales_data.csv"
VISUALS_DIR = "/home/claude/retail-sales-analysis/visuals"

plt.style.use("seaborn-v0_8-whitegrid")
COLOR = "#2E86AB"

def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["order_date"])

def revenue_by_month(df):
    monthly = df.groupby("month")["revenue"].sum().sort_index()
    fig, ax = plt.subplots(figsize=(9, 5))
    monthly.plot(kind="line", marker="o", ax=ax, color=COLOR)
    ax.set_title("Monthly Revenue Trend (2025)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (Rs.)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    fig.savefig(f"{VISUALS_DIR}/monthly_revenue_trend.png", dpi=150)
    plt.close(fig)
    return monthly

def revenue_by_region(df):
    region_rev = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    region_rev.plot(kind="bar", ax=ax, color=COLOR)
    ax.set_title("Total Revenue by Region")
    ax.set_xlabel("Region")
    ax.set_ylabel("Revenue (Rs.)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    fig.savefig(f"{VISUALS_DIR}/revenue_by_region.png", dpi=150)
    plt.close(fig)
    return region_rev

def revenue_by_category(df):
    cat_rev = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    cat_rev.plot(kind="barh", ax=ax, color=COLOR)
    ax.set_title("Revenue by Product Category")
    ax.set_xlabel("Revenue (Rs.)")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    fig.savefig(f"{VISUALS_DIR}/revenue_by_category.png", dpi=150)
    plt.close(fig)
    return cat_rev

def top_products(df, n=10):
    top = df.groupby("product_name")["revenue"].sum().sort_values(ascending=False).head(n)
    fig, ax = plt.subplots(figsize=(8, 5))
    top.sort_values().plot(kind="barh", ax=ax, color=COLOR)
    ax.set_title(f"Top {n} Products by Revenue")
    ax.set_xlabel("Revenue (Rs.)")
    plt.tight_layout()
    fig.savefig(f"{VISUALS_DIR}/top_products.png", dpi=150)
    plt.close(fig)
    return top

def segment_share(df):
    seg = df.groupby("customer_segment")["revenue"].sum()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(seg, labels=seg.index, autopct="%1.1f%%", startangle=90,
           colors=["#2E86AB", "#A23B72", "#F18F01", "#5C946E"])
    ax.set_title("Revenue Share by Customer Segment")
    plt.tight_layout()
    fig.savefig(f"{VISUALS_DIR}/segment_share.png", dpi=150)
    plt.close(fig)
    return seg

def print_insights(df, monthly, region_rev, cat_rev, top, seg):
    total_revenue = df["revenue"].sum()
    total_orders = len(df)
    avg_order_value = total_revenue / total_orders

    print("\n" + "=" * 50)
    print("KEY INSIGHTS")
    print("=" * 50)
    print(f"Total Revenue        : ₹{total_revenue:,.0f}")
    print(f"Total Orders         : {total_orders:,}")
    print(f"Avg. Order Value     : ₹{avg_order_value:,.0f}")
    print(f"Best Month           : {monthly.idxmax()} (₹{monthly.max():,.0f})")
    print(f"Weakest Month        : {monthly.idxmin()} (₹{monthly.min():,.0f})")
    print(f"Top Region           : {region_rev.idxmax()} (₹{region_rev.max():,.0f})")
    print(f"Top Category         : {cat_rev.idxmax()} (₹{cat_rev.max():,.0f})")
    print(f"Best-Selling Product : {top.idxmax()} (₹{top.max():,.0f})")
    print(f"Leading Segment      : {seg.idxmax()} ({seg.max()/seg.sum()*100:.1f}% of revenue)")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    df = load_data()
    monthly = revenue_by_month(df)
    region_rev = revenue_by_region(df)
    cat_rev = revenue_by_category(df)
    top = top_products(df)
    seg = segment_share(df)
    print_insights(df, monthly, region_rev, cat_rev, top, seg)
    print(f"Charts saved to {VISUALS_DIR}/")
