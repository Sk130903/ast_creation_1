import pandas as pd
from utility_functions import (
    calculate_tax,
    categorize_purchase_channel,
    calculate_loyalty_points,
)

# -------- Cell 1 --------
orders = pd.DataFrame({
    "order_id": list(range(101, 121)),
    "customer_id": [1, 2, 3, 4, 5, 1, 6, 7, 8, 9, 2, 10, 11, 12, 13, 14, 3, 15, 16, 4],
    "order_amount": [
        120, 340, 75, 900, 60, 210, 1500, 45, 310, 88,
        420, 990, 33, 275, 610, 1800, 95, 150, 2200, 720,
    ],
    "channel": [
        "web", "app", "store", "online", "mobile", "call_center", "website", "in-store",
        "android", "ios", "phone", "web", "retail", "app", "unknown", "web",
        "store", "mobile", "online", "app",
    ],
    "state_or_country": [
        "CA", "NY", "TX", "international", "WA", "CA", "international", "NY",
        "TX", "WA", "CA", "international", "NY", "TX", "XX", "CA",
        "TX", "WA", "international", "international",
    ],
    "order_date": pd.to_datetime([
        "2026-01-03", "2026-01-05", "2026-01-05", "2026-01-07", "2026-01-09",
        "2026-01-12", "2026-01-14", "2026-01-15", "2026-01-16", "2026-01-18",
        "2026-01-20", "2026-01-22", "2026-01-23", "2026-01-25", "2026-01-27",
        "2026-01-29", "2026-02-01", "2026-02-02", "2026-02-04", "2026-02-05",
    ]),
})


def compute_order_tax(order_amount, state_or_country):
    '''Thin wrapper around the shared tax lookup, kept here so order-level reporting
    doesn't need to import the full customer pipeline.'''
    return calculate_tax(order_amount, state_or_country)


def bucket_order_size(order_amount):
    '''Classify an order into a coarse size bucket used for reporting dashboards.'''
    if order_amount >= 1000:
        return "large"
    elif order_amount >= 300:
        return "medium"
    elif order_amount >= 100:
        return "small"
    return "micro"


def detect_repeat_customers(df):
    '''Return the set of customer_ids that placed more than one order in this batch.'''
    counts = df["customer_id"].value_counts()
    return sorted(counts[counts > 1].index.tolist())


def calculate_order_velocity(df, window_days=7):
    '''Average number of orders placed per rolling window across the observed date range.'''
    if df.empty:
        return 0.0
    span_days = (df["order_date"].max() - df["order_date"].min()).days + 1
    n_windows = max(span_days / window_days, 1)
    return round(len(df) / n_windows, 2)


def detect_seasonal_spike(df, threshold_multiplier=1.5):
    '''Flag days whose order volume is well above the batch's average daily volume.'''
    daily_counts = df.groupby(df["order_date"].dt.date).size()
    if daily_counts.empty:
        return []
    avg = daily_counts.mean()
    spikes = daily_counts[daily_counts >= avg * threshold_multiplier]
    return [{"date": str(d), "order_count": int(c)} for d, c in spikes.items()]


def build_order_summary(df):
    '''Assemble the top-level order analytics summary used by the dashboard.'''
    enriched = df.copy()
    enriched["size_bucket"] = enriched["order_amount"].apply(bucket_order_size)
    enriched["channel_category"] = enriched["channel"].apply(categorize_purchase_channel)
    enriched["tax"] = enriched.apply(
        lambda row: compute_order_tax(row["order_amount"], row["state_or_country"]), axis=1
    )

    return {
        "total_orders": len(enriched),
        "total_revenue": round(enriched["order_amount"].sum(), 2),
        "repeat_customers": detect_repeat_customers(enriched),
        "order_velocity_per_week": calculate_order_velocity(enriched),
        "seasonal_spikes": detect_seasonal_spike(enriched),
        "by_size_bucket": enriched["size_bucket"].value_counts().to_dict(),
        "by_channel": enriched["channel_category"].value_counts().to_dict(),
    }


# -------- Cell 2 --------
orders["size_bucket"] = orders["order_amount"].apply(bucket_order_size)

# -------- Cell 3 --------
orders["channel_category"] = orders["channel"].apply(categorize_purchase_channel)

# -------- Cell 4 --------
orders["tax"] = orders.apply(
    lambda row: compute_order_tax(row["order_amount"], row["state_or_country"]), axis=1
)

# -------- Cell 5 --------
order_summary = build_order_summary(orders)

print(orders)
print(order_summary)
