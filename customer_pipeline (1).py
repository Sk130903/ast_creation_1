import pandas as pd
from utility_functions import (
    clean_customer_names,
    calculate_final_amount,
    assign_customer_tier,
    validate_email,
    normalize_phone_number,
    calculate_loyalty_points,
    categorize_purchase_channel,
    compute_shipping_cost,
    is_valid_postal_code,
    calculate_tax,
    generate_customer_id,
    deduplicate_customers,
    flag_high_risk_transaction,
    summarize_customer_batch,
)

# -------- Cell 1 --------
customers = pd.DataFrame({
    "customer_id": list(range(1, 17)),
    "customer_name": [
        " alice ", "BOB", None, "charlie", "Diana Prince", "  evan  ", "Fiona", "george",
        "Hannah ", "Ian", None, "Julia Roberts", " Kevin", "laura", "Mallory", "alice ",
    ],
    "purchase_amount": [
        1200, 650, 300, 1800, 90, 520, 2200, 175,
        980, 40, 610, 1350, 260, 3100, 15, 1200,
    ],
    "email": [
        "alice@test.com", "bob@test.com", "invalid_email", "charlie@test.com",
        "diana@heroes.io", "evan_at_test", "fiona@shop.com", "george@shop.com",
        "hannah@retail.net", None, "ian@@bad.com", "julia@studio.com",
        "kevin@mail.co", "laura@mail.co", "mallory@bad", "alice@test.com",
    ],
    "phone": [
        "(555) 123-4567", "555.234.5678", "not-a-phone", "5553456789",
        "555 456 7890", "12345", "+1-555-567-8901", "555-678-9012",
        "5556789013", "n/a", "555 789 0124", "(555) 890-1235",
        "555-901-2346", "5559012347", "123", "(555) 123-4567",
    ],
    "channel": [
        "web", "App", "store", "Online", "mobile", "call_center", "Website", "IN-STORE",
        "android", "ios", "phone", "web", "retail", "app", "unknown_channel", "web",
    ],
    "region": [
        "domestic", "north_america", "domestic", "international", "domestic", "domestic",
        "international", "domestic", "north_america", "domestic", "domestic",
        "international", "domestic", "north_america", "domestic", "domestic",
    ],
    "state_or_country": [
        "CA", "NY", "TX", "international", "WA", "CA", "international", "NY",
        "TX", "WA", "CA", "international", "NY", "TX", "XX", "CA",
    ],
    "postal_code": [
        "94105", "10001", "73301-1234", "SW1A 1AA", "98101", "94105", "M5V 3L9", "10001",
        "73301", "98101", "9410X", "EC1A 1BB", "10001", "73301", "000", "94105",
    ],
})

# -------- Cell 2 --------
customers = clean_customer_names(customers)

# -------- Cell 3 --------
customers["phone_normalized"] = customers["phone"].apply(normalize_phone_number)

# -------- Cell 4 --------
customers["final_amount"] = customers["purchase_amount"].apply(calculate_final_amount)

# -------- Cell 5 --------
customers["tier"] = customers["purchase_amount"].apply(assign_customer_tier)

# -------- Cell 6 --------
customers["loyalty_points"] = customers.apply(
    lambda row: calculate_loyalty_points(row["purchase_amount"], row["tier"]), axis=1
)

# -------- Cell 7 --------
customers["email_valid"] = customers["email"].apply(validate_email)

# -------- Cell 8 --------
customers["channel_category"] = customers["channel"].apply(categorize_purchase_channel)

# -------- Cell 9 --------
customers["shipping_cost"] = customers.apply(
    lambda row: compute_shipping_cost(row["purchase_amount"], row["region"]), axis=1
)

# -------- Cell 10 --------
customers["postal_valid"] = customers.apply(
    lambda row: is_valid_postal_code(row["postal_code"], row["state_or_country"] if row["state_or_country"] in ("US",) else "US"),
    axis=1,
)

# -------- Cell 11 --------
customers["tax"] = customers.apply(
    lambda row: calculate_tax(row["purchase_amount"], row["state_or_country"]), axis=1
)

# -------- Cell 12 --------
customers["customer_uid"] = customers.apply(
    lambda row: generate_customer_id(row["customer_name"], row["customer_id"]), axis=1
)

# -------- Cell 13 --------
customers["risk_level"] = customers.apply(
    lambda row: flag_high_risk_transaction(row["purchase_amount"], row["state_or_country"], row["email_valid"]),
    axis=1,
)

# -------- Cell 14 --------
customers_deduped = deduplicate_customers(customers)

# -------- Cell 15 --------
summary = (
    customers_deduped.groupby("tier")
    .agg(
        customers=("customer_id", "count"),
        revenue=("final_amount", "sum"),
        avg_loyalty_points=("loyalty_points", "mean"),
    )
    .reset_index()
)

# -------- Cell 16 --------
channel_summary = (
    customers_deduped.groupby("channel_category")
    .agg(customers=("customer_id", "count"), revenue=("final_amount", "sum"))
    .reset_index()
)

# -------- Cell 17 --------
risk_summary = customers_deduped["risk_level"].value_counts().reset_index()
risk_summary.columns = ["risk_level", "count"]

# -------- Cell 18 --------
overall_summary = summarize_customer_batch(customers_deduped)

print(customers_deduped)
print(summary)
print(channel_summary)
print(risk_summary)
print(overall_summary)
